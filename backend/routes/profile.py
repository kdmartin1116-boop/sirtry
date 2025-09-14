from flask import Blueprint, request, jsonify
from modules.database import get_profile, save_profile

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile_route():
    profile = get_profile()
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Profile not found"}), 404

@profile_bp.route('/api/profile', methods=['POST'])
def save_profile_route():
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    email = data.get('email')
    phone = data.get('phone')
    
    save_profile(name, address, email, phone)
    
    return jsonify({"message": "Profile saved successfully"})
