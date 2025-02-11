from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
from app import mongo
from app.utils.logger import logger
from app.utils.decorators import timing_decorator

# Define Blueprint
token_jwt_bp = Blueprint('token', __name__)

@token_jwt_bp.route('/generate', methods=['POST'])
@timing_decorator
@jwt_required()
def generate_token():
    """Generates a token for the authenticated user."""
    try:
        current_user = get_jwt_identity()
        logger.info(f"Token request from user: {current_user}")

        # Example: Generate a new token with a 1-hour expiry
        new_token = create_access_token(identity=current_user, expires_delta=timedelta(hours=1))

        return jsonify({'token': new_token, 'expires_in': 3600}), 200

    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@token_jwt_bp.route('/validate', methods=['GET'])
@timing_decorator
@jwt_required()
def validate_token():
    """Validates a JWT token and returns user identity."""
    try:
        current_user = get_jwt_identity()
        logger.info(f"Token validated for user: {current_user}")

        return jsonify({'message': 'Token is valid', 'user': current_user}), 200

    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return jsonify({'message': 'Invalid token', 'error': str(e)}), 401
@token_jwt_bp.route('/tokens', methods=['GET'])
@jwt_required()
def get_tokens():
    try:
        user_id = get_jwt_identity()
        tokens = APIToken.get_user_tokens(user_id)

        return jsonify({
            'tokens': [{
                'id': str(token['_id']),
                'name': token['name'],
                'token': token['token'],
                'created_at': token['created_at'],
                'expires_at': token['expires_at'],
                'last_used': token['last_used'],
                'is_active': token['is_active']
            } for token in tokens]
        }), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@token_jwt_bp.route('/tokens', methods=['POST'])
@jwt_required()
def create_token():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Token name is required'}), 400

        token_name = data['name'].strip()
        if not token_name:
            return jsonify({'message': 'Token name cannot be empty'}), 400

        user_id = get_jwt_identity()
        expires_at = datetime.utcnow() + timedelta(days=30)

        token = APIToken.create(user_id, token_name, expires_at)

        if not isinstance(token, dict):
            return jsonify({'message': 'Token creation failed'}), 500

        return jsonify({
            'message': 'Token created successfully',
            'token': {
                'id': str(token['_id']),
                'name': token['name'],
                'token': token['token'],
                'created_at': token['created_at'],
                'expires_at': token['expires_at'],
                'last_used': token['last_used'],
                'is_active': token['is_active']
            }
        }), 201
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

 
  