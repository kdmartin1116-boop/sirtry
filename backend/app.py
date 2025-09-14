from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, url_for
import os
import sys
import yaml
import json
from datetime import datetime
from pypdf import PdfReader
import pytesseract
from PIL import Image # Added from app (2).py

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- MODULES FROM ENDORSEMENT ENGINE ---
from modules.Ucc3_Endorsements import sign_endorsement
from modules.remedy_logger import log_remedy
from modules.bill_parser import BillParser
from modules.attach_endorsement_to_pdf import attach_endorsement_to_pdf_function, stamp_pdf_with_endorsement
from modules.database import init_db
from modules.utils import load_yaml_config, get_bill_data_from_source, prepare_endorsement_for_signing # Imported helper functions

# --- ERROR HANDLING AND LOGGING SUGGESTIONS ---
# 1. Centralized Error Handling: Implement a global error handler for Flask
#    applications (e.g., using @app.errorhandler(Exception) or
#    @app.errorhandler(HTTPException)) to catch unhandled exceptions and
#    return consistent JSON error responses.
# 2. Structured Logging: Ensure `remedy_logger` (or a more standard logging
#    setup) provides structured logging (e.g., JSON format) with appropriate
#    log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) and context
#    (request ID, user ID, etc.).
# 3. Specific Exception Handling: Where possible, catch more specific exceptions
#    rather than broad `Exception` to provide more precise error messages
#    and recovery.

# --- BLUEPRINTS ---
from routes.profile import profile_bp
from routes.credit_report import credit_report_bp
from routes.disputes import disputes_bp
from routes.vehicle import vehicle_bp
from routes.endorsement import endorsement_bp
from routes.legal import legal_bp
from routes.generator_routes import generator_bp # Assuming this is the correct name for the blueprint in generator_routes.py

# --- API DOCUMENTATION SUGGESTION ---
# For comprehensive API documentation (e.g., Swagger/OpenAPI), consider integrating
# a Flask extension like Flask-RESTX or Flask-Smorest. This would allow for
# automatic generation of interactive API documentation from your route definitions.
# Example: from flask_restx import Api, Resource
# api = Api(app, version='1.0', title='Backend API', description='A simple API')
# namespace = api.namespace('YourResource', description='Your operations')
# @namespace.route('/your-endpoint')
# class YourResource(Resource):
#    def get(self):
#        return {'message': 'Hello from API'}


# Disable default static serving
app = Flask(__name__, static_folder=None, template_folder='templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Register Blueprints
app.register_blueprint(profile_bp)
app.register_blueprint(credit_report_bp)
app.register_blueprint(disputes_bp)
app.register_blueprint(vehicle_bp)
app.register_blueprint(endorsement_bp)
app.register_blueprint(legal_bp)
app.register_blueprint(generator_bp) # Register the generator blueprint

# --- CONFIGURATION ---
# Load the private key from an environment variable for security or from file
PRIVATE_KEY_PEM = os.environ.get("PRIVATE_KEY_PEM")
if not PRIVATE_KEY_PEM:
    private_key_file_path = os.environ.get("PRIVATE_KEY_PATH", "config/private_key.pem")
    try:
        with open(private_key_file_path, "r") as f:
            PRIVATE_KEY_PEM = f.read()
    except FileNotFoundError:
        PRIVATE_KEY_PEM = None # Or handle the error as appropriate
SOVEREIGN_OVERLAY_CONFIG = os.environ.get("SOVEREIGN_OVERLAY_CONFIG_PATH", "config/sovereign_overlay.yaml")


# New route to serve files from the dist directory
@app.route('/static/dist/<path:filename>')
def serve_dist_files(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'frontend', 'dist'), filename)

# Explicitly serve the main static folder (for style.css etc.)
@app.route('/static/<path:filename>', endpoint='static')
def serve_static_files(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'legacy-frontend', 'static'), filename)

@app.route('/')
def index():
    script_url = None
    if app.debug: # Force development fallback when in debug mode
        script_url = None
    else:
        manifest_path = os.path.join(app.root_path, 'static', 'dist', '.vite', 'manifest.json')
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
                # The key in the manifest is the source file name, e.g., 'static/main.js'
                script_entry = manifest.get('static/main.js')
                if script_entry:
                    script_file = script_entry['file']
                    script_url = url_for('serve_dist_files', filename=script_file)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass # Fallback to None if manifest not found or invalid

    return render_template('test.html')

@app.route('/scan-contract', methods=['POST'])
def scan_contract():
    file = request.files['contract']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Unsupported file type. Please upload a PDF."} ), 400
    tag = request.form['tag']
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    output = f"Scanning contract: {filepath} for tags: {tag}\n(pdftotext is installed, but actual scanning logic is not yet implemented)"
    return jsonify({'output': output})

@app.route('/endorse-bill', methods=['POST'])
def endorse_bill():
    if not PRIVATE_KEY_PEM:
        return jsonify({"error": "Server is not configured with a private key."} ), 500

    if 'bill' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['bill']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Unsupported file type. Please upload a PDF."} ), 400

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, file.filename)
    file.save(filepath)

    try:
        bill_data = get_bill_data_from_source(filepath)
        if "error" in bill_data:
            return jsonify(bill_data), 500

        # Check if SOVEREIGN_OVERLAY_CONFIG file exists
        if not os.path.exists(SOVEREIGN_OVERLAY_CONFIG):
            return jsonify({"error": f"Configuration file not found: {SOVEREIGN_OVERLAY_CONFIG}"}), 500

        overlay_config = load_yaml_config(SOVEREIGN_OVERLAY_CONFIG)
        if "error" in overlay_config:
            # This means there was a YAML parsing error
            return jsonify(overlay_config), 500
        else:
            sovereign_endorsements = overlay_config.get("sovereign_endorsements", [])

        if not sovereign_endorsements:
            return jsonify({"message": "Bill processed, but no applicable endorsements found in config."} ), 200

        endorsed_files = []
        for endorsement_type in sovereign_endorsements:
            trigger = endorsement_type.get("trigger", "Unknown")
            meaning = endorsement_type.get("meaning", "")
            ink_color = endorsement_type.get("ink_color", "black")
            placement = endorsement_type.get("placement", "Front")
            page_index = 0 if placement.lower() == "front" else -1

            endorsement_text = f"{trigger}: {meaning}"
            endorsement_to_sign = prepare_endorsement_for_signing(bill_data, endorsement_text)

            signed_endorsement = sign_endorsement(
                endorsement_data=endorsement_to_sign,
                endorser_name=bill_data.get("customer_name", "N/A"),
                private_key_pem=PRIVATE_KEY_PEM
            )

            bill_for_logging = {
                "instrument_id": bill_data.get("bill_number"),
                "issuer": bill_data.get("issuer", "Unknown"),
                "recipient": bill_data.get("customer_name"),
                "amount": bill_data.get("total_amount"),
                "currency": bill_data.get("currency"),
                "description": bill_data.get("description", "N/A"),
                "endorsements": [{
                    "endorser_name": signed_endorsement.get("endorser_id"),
                    "text": endorsement_text,
                    "next_payee": "Original Creditor",
                    "signature": signed_endorsement["signature"]
                }],
                "signature_block": {
                    "signed_by": signed_endorsement.get("endorser_id"),
                    "capacity": "Payer",
                    "signature": signed_endorsement["signature"],
                    "date": signed_endorsement.get("endorsement_date")
                }
            }

            log_remedy(bill_for_logging)

            output_pdf_name = f"endorsed_{os.path.basename(filepath).replace('.pdf', '')}_{trigger.replace(' ', '')}.pdf"
            endorsed_output_path = os.path.join(uploads_dir, output_pdf_name)

            attach_endorsement_to_pdf_function(
                original_pdf_path=filepath,
                endorsement_data=bill_for_logging,
                output_pdf_path=endorsed_output_path,
                ink_color=ink_color,
                page_index=page_index
            )
            endorsed_files.append(output_pdf_name)

        return jsonify({"message": "Bill endorsed successfully", "endorsed_files": endorsed_files})

    except FileNotFoundError as e:
        return jsonify({"error": f"File not found: {e}"}), 500
    except yaml.YAMLError as e:
        return jsonify({"error": f"YAML parsing error in configuration: {e}"}), 500
    except Exception as e:
        # Catch any other unexpected errors
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/stamp_endorsement', methods=['POST'])
def stamp_endorsement_route():
    if 'bill' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['bill']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Unsupported file type. Please upload a PDF."} ), 400

    x = float(request.form.get('x', 0))
    y = float(request.form.get('y', 0))
    endorsement_text = request.form.get('endorsement_text', '')
    qualifier = request.form.get('qualifier', '')

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    original_filepath = os.path.join(uploads_dir, file.filename)
    file.save(original_filepath)

    output_filename = f"stamped_{file.filename}"
    output_filepath = os.path.join(uploads_dir, output_filename)

    success = stamp_pdf_with_endorsement(
        original_pdf_path=original_filepath,
        output_pdf_path=output_filepath,
        x=x,
        y=y,
        endorsement_text=endorsement_text,
        qualifier=qualifier
    )

    if success:
        return send_file(output_filepath, as_attachment=True, download_name=output_filename)
    else:
        return jsonify({"error": "Failed to stamp PDF"}), 500

@app.route('/generate-tender-letter', methods=['POST'])
def generate_tender_letter():
    data = request.get_json()
    user_name = data.get('userName')
    user_address = data.get('userAddress')
    creditor_name = data.get('creditorName')
    creditor_address = data.get('creditorAddress')
    bill_file_name = data.get('billFileName')

    if not all([user_name, user_address, creditor_name, creditor_address, bill_file_name]):
          return jsonify({"error": "Missing required data for tender letter generation."} ), 400      
    today = datetime.now().strftime("%B %d, %Y")

    tender_letter_content = f"""
*** DISCLAIMER: This letter is based on pseudo-legal theories associated with the \"sovereign citizen\" movement. These theories are not recognized in mainstream commercial law and may have adverse legal consequences. Use at your own risk. ***

[Your Name: {user_name}]
[Your Address: {user_address}]

{today}

TO: {creditor_name}
    {creditor_address}

SUBJECT: Private Administrative Process - Tender of Payment for Instrument {bill_file_name}

Dear Sir/Madam,

This correspondence serves as a formal tender of payment, presented in good faith, for the instrument identified as \"{bill_file_name}\". This instrument, having been properly endorsed and accepted for value, is hereby presented as a valid and lawful tender for the discharge and settlement of any alleged obligation or account associated therewith.

Be advised that this tender is made in accordance with the principles of commercial law and equity. Under Uniform Commercial Code (UCC) 3-603, a tender of payment of an obligation to pay an instrument made to a person entitled to enforce the instrument, if refused, discharges the obligation of the obligor to pay interest on the obligation after the due date and discharges any party with a right of recourse against the obligor to the extent of the amount of the tender.

Your refusal to accept this lawful tender of payment will be considered a dishonor of a commercial instrument and a refusal of a valid tender. All rights, remedies, and recourse, both at law and in equity, are expressly reserved without prejudice, pursuant to UCC 1-308.

This is a private administrative process. Your acceptance of this tender, or your failure to return the instrument with specific objections within [e.g., 3, 7, 10] days, will be deemed as acceptance of this tender and agreement to the discharge of the obligation.

Sincerely,

By: {user_name}
Authorized Representative / Agent
All Rights Reserved. Without Prejudice. UCC 1-308.
"""
    return jsonify({"letterContent": tender_letter_content.strip()}), 200

@app.route('/generate-ptp-letter', methods=['POST'])
def generate_ptp_letter():
    data = request.get_json(force=True)
    user_name = data.get('userName')
    user_address = data.get('userAddress')
    creditor_name = data.get('creditorName')
    creditor_address = data.get('creditorAddress')
    account_number = data.get('accountNumber')
    promise_amount = data.get('promiseAmount')
    promise_date = data.get('promiseDate')

    if not all([user_name, user_address, creditor_name, creditor_address, account_number, promise_amount, promise_date]):
        return jsonify({"error": "Missing required data for Promise to Pay letter generation."} ), 400

    today = datetime.now().strftime("%B %d, %Y")
    # Format promise_date for display
    formatted_promise_date = datetime.strptime(promise_date, '%Y-%m-%d').strftime("%B %d, %Y")

    ptp_letter_content = f"""
[Your Name: {user_name}]
[Your Address: {user_address}]

{today}

TO: {creditor_name}
    {creditor_address}

SUBJECT: Promise to Pay - Account: {account_number}

Dear {creditor_name},

This letter serves as my formal commitment to pay the outstanding amount on the account referenced above.

I, {user_name}, hereby promise to pay the amount of ${promise_amount} on or before {formatted_promise_date}.

This payment is being made to settle the account. Please update your records accordingly upon receipt of the payment. I request that you provide written confirmation of the payment being received and the account being settled.

Thank you for your understanding in this matter.

Sincerely,

{user_name}
"""
    return jsonify({"letterContent": ptp_letter_content.strip()}), 200


@app.route('/get-bill-data', methods=['POST'])
def get_bill_data():
    if 'bill' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['bill']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Unsupported file type. Please upload a PDF."} ), 400

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, file.filename)
    file.save(filepath)

    try:
        bill_data = get_bill_data_from_source(filepath)
        if "error" in bill_data:
            return jsonify(bill_data), 500
        return jsonify(bill_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to extract bill data: {str(e)}"}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/scan-for-terms', methods=['POST'])
def scan_for_terms():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    tag = request.form.get('tag')

    if not file or not tag:
        return jsonify({"error": "Missing file or tag"}), 400

    # Define keyword mappings
    keyword_map = {
        "hidden_fee": ["convenience fee", "service charge", "processing fee", "undisclosed", "surcharge"],
        "misrepresentation": ["misrepresented", "misleading", "deceptive", "false statement", "inaccurate"],
        "arbitration": ["arbitration", "arbitrator", "binding arbitration", "waive your right to"]
    }

    keywords = keyword_map.get(tag, [])
    if not keywords:
        return jsonify({"error": "Invalid tag specified"}), 400

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    filepath = os.path.join(uploads_dir, file.filename)
    file.save(filepath)

    try:
        # Simplified text extraction
        text = ""
        with open(filepath, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        
        if not text.strip():
            return jsonify({"error": "Could not extract text from PDF."} ), 500

        # Search for keywords in sentences
        found_sentences = []
        sentences = text.replace('\n', ' ').split('. ')

        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence.lower():
                    found_sentences.append(sentence.strip() + ".")
                    break 
        
        return jsonify({"found_clauses": found_sentences})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route('/generate-remedy', methods=['POST'])
def generate_remedy():
    violation = request.form['violation']
    jurisdiction = request.form['jurisdiction']
    output = f"Generating remedy for violation: {violation} in jurisdiction: {jurisdiction}\n(Remedy generation logic is not yet implemented)"
    return jsonify({'output': output})

# --- TESTING SUGGESTIONS ---
# 1. Test Coverage: Use a tool like `coverage.py` to measure test coverage and
#    aim for a high percentage to ensure critical code paths are tested.
# 2. CI/CD Integration: Integrate tests into a Continuous Integration/Continuous
#    Deployment (CI/CD) pipeline to run tests automatically on every code change.
# 3. Mocking/Stubbing: Employ mocking/stubbing techniques for external dependencies
#    (e.g., database, external APIs) to make unit tests faster and more reliable.

if __name__ == '__main__':
    init_db()
    os.makedirs('uploads', exist_ok=True)
    app.run(host='127.0.0.1', port=8000, debug=True)

# --- DEPLOYMENT SUGGESTIONS ---
# 1. Production Server: For production deployments, use a robust WSGI server
#    like Gunicorn (for Linux) or Waitress (for Windows) to serve the Flask app.
#    Example (Gunicorn): gunicorn -w 4 -b 0.0.0.0:8000 app:app
# 2. Reverse Proxy: Place a reverse proxy (e.g., Nginx, Apache) in front of the
#    WSGI server to handle static files, SSL termination, load balancing, etc.
# 3. Containerization: Consider containerizing the application using Docker.
#    This provides consistency across environments and simplifies deployment.
#    A Dockerfile would define the environment and dependencies.
# 4. Cloud Platforms: Deploy to cloud platforms like AWS (EC2, Elastic Beanstalk),
#    Google Cloud (App Engine, Compute Engine), or Azure.