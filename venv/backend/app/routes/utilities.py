# routes/utilities.py
from flask import request
import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from app.services.utility_service import UtilityService  
from app import mongo
from http import HTTPStatus
from datetime import datetime

utilities_bp = Blueprint('utilities', __name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@utilities_bp.route("/utility_unit_price", methods=["GET", "OPTIONS"])
@jwt_required()
 
def get_utility_prices():
    """API to fetch current utility prices."""
    # if request.method == "OPTIONS":
    #     response = jsonify({'message': 'Preflight successful'})
    #     response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    #     response.headers.add('Access-Control-Allow-Credentials', 'true')
    #     return response, HTTPStatus.OK

    prices = {
        "water": UtilityService.get_unit_price("water"),
        "gas": UtilityService.get_unit_price("gas"),
        "energy": UtilityService.get_unit_price("energy"),
    }
    return jsonify(prices), HTTPStatus.OK
 
@utilities_bp.route('/balances', methods=['GET'])
@jwt_required()
def get_utility_balances():
    try:
        user_email = get_jwt_identity()
        # print("User Email:", user_email)
        balances = UtilityService.get_utility_balances(user_email)
        
        return jsonify({
            'utilities': [balance.__dict__ for balance in balances]
        }), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@utilities_bp.route('/all-balances', methods=['GET'])
@jwt_required()
def get_all_utility_balances():
    try:
        user_email = get_jwt_identity()
        balances = UtilityService.get_all_utility_balances(user_email)
        
        return jsonify({
            'utilities': balances
        }), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@utilities_bp.route('/specific-utility-balance', methods=['GET'])
@jwt_required()
def get_specific_utility_balance():
    try:
        # Retrieve the user email from the JWT token
        user_email = get_jwt_identity()

        # Get the utility type from query parameter (e.g., ?utility_type=gas)
        utility_type = request.args.get('utility_type')

        # Check if the utility type is valid
        if utility_type not in ['gas', 'water', 'energy']:
            return jsonify({
                'message': 'Invalid utility type',
                'error': 'Valid types are gas, water, or energy'
            }), HTTPStatus.BAD_REQUEST

        # Fetch the utility balance from the respective collection
        balance = UtilityService.get_specific_utility_balance(user_email, utility_type)

        # Debugging logs
        print(f"Final Balance Returned: {balance}")

        # Ensure balance is correctly formatted
        return jsonify({
            'utility_type': utility_type,
            'balance': int(balance)  # Convert to int to prevent serialization issues
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


    
@utilities_bp.route('/get_monthly_utility_data', methods=['GET'])
@jwt_required()
def get_monthly_utility_data():

    try:
        user_email = get_jwt_identity()
        # logging.debug(f"Fetching monthly utility data for user: {user_email}")
        monthly_data = UtilityService.get_monthly_utility_data(user_email)
        # logging.debug(f"Monthly data: {monthly_data}")
        
        return jsonify({
            'utilities': monthly_data
        }), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    

 # routes/utility_routes.py

import re
from flask import jsonify

def is_valid_token(recharge_token):
    """Validate the token format (should be 16 digits grouped as XXXX-XXXX-XXXX-XXXX)"""
    return bool(re.match(r"^\d{4}-\d{4}-\d{4}-\d{4}$", recharge_token))
 

@utilities_bp.route('/process-meter-recharge', methods=['POST'])
def process_meter_recharge():
    try:
        data = request.json

        # Validate required fields FIRST
        required_fields = ['user_email', 'utility_type', 'token', 'units', 'timestamp']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        recharge_token = data["token"]

        # Validate token format
        if not is_valid_token(recharge_token):
            return jsonify({"error": "Invalid token format"}), 400

        # Debugging print
        print(f"Received data: {data}")

        # Get current utility balance
        utilities_balance = mongo.db.utilities_balance
        current_balance = utilities_balance.find_one({
            'user_email': data['user_email'],
            'utility_type': data['utility_type']
        })

        if not current_balance:
            return jsonify({'error': 'Utility balance record not found'}), 404

        # Update utility balance
        result = utilities_balance.update_one(
            {
                'user_email': data['user_email'],
                'utility_type': data['utility_type']
            },
            {
                '$inc': {'units': -data['units']},
                '$push': {
                    'recharge_history': {
                        'token': data['token'],
                        'units': data['units'],
                        'timestamp': datetime.fromisoformat(data['timestamp'])
                    }
                },
                '$set': {'last_updated': datetime.utcnow()}
            }
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update utility balance'}), 500

        return jsonify({
            'message': 'Recharge processed successfully',
            'units_deducted': data['units']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add the blueprint to your Flask app
# In your main app.py:
# from routes.utility_routes import utility_bp
# app.register_blueprint(utility_bp)   