# routes/dashboard.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from app.services.user_service import UserService
from app.services.utility_service import UtilityService
from app.services.transactions_service1 import TransactionService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        profile = UserService.get_profile(user_id)
        
        if not profile:
            return jsonify({'message': 'User not found'}), HTTPStatus.NOT_FOUND
            
        return jsonify({'profile': profile.__dict__}), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@dashboard_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'message': 'No data provided'
            }), HTTPStatus.BAD_REQUEST
            
        success = UserService.update_profile(user_id, data)
        
        if not success:
            return jsonify({
                'message': 'No valid fields to update'
            }), HTTPStatus.BAD_REQUEST
            
        return jsonify({
            'message': 'Profile updated successfully',
            'updatedProfile': data
        }), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard_data():
    try:
        user_id = get_jwt_identity()
        
        data = {
            "utilities": [stat.__dict__ for stat in 
                         UtilityService.get_utility_stats(user_id)],
            "transactions": TransactionService.get_recent_transactions(user_id),
            "monthlySummary": TransactionService.get_monthly_summary(user_id)
        }
        
        return jsonify(data), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR