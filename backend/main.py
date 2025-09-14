from bill_parser import parse_bill
from endorsement_engine import classify_instrument, apply_endorsement
from signature_agent import sign_as_agent
from remedy_logger import log_remedy

# Load sample bill
bill_path = "sample_bills/utility_bill.json"
bill = parse_bill(bill_path)

# Classify instrument type
instrument_type = classify_instrument(bill)

# Apply endorsement
endorsement_text = "Accepted for Value and Returned for Value"
endorsed_bill = apply_endorsement(bill, instrument_type, endorsement_text)

# Sign as agent
signed_bill = sign_as_agent(endorsed_bill, agent_name="Michaela Martin", principal="Michaela Martin")

# Log remedy
log_remedy(signed_bill)

print("✅ Endorsement complete. Remedy logged.")