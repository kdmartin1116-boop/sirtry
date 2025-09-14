from flask import Blueprint, request, jsonify
from modules.database import get_all_disputes, add_dispute, update_dispute_status
from datetime import datetime

disputes_bp = Blueprint('disputes_bp', __name__)

@disputes_bp.route('/api/disputes', methods=['GET'])
def get_disputes_route():
    disputes = get_all_disputes()
    return jsonify(disputes)

@disputes_bp.route('/api/disputes', methods=['POST'])
def add_dispute_route():
    data = request.get_json()
    account_name = data.get('account_name')
    account_number = data.get('account_number')
    date_sent = datetime.now().strftime("%Y-%m-%d")
    status = "Sent"
    
    add_dispute(account_name, account_number, date_sent, status)
    
    return jsonify({"message": "Dispute tracked successfully"})

@disputes_bp.route('/api/disputes/<int:dispute_id>', methods=['PUT'])
def update_dispute_route(dispute_id):
    data = request.get_json()
    status = data.get('status')
    
    update_dispute_status(dispute_id, status)
    
    return jsonify({"message": "Dispute status updated successfully"})
