
# app/routes/auth.py
from flask import Blueprint, request, jsonify, url_for
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from app.utils.email import send_verification_email
from datetime import datetime, timedelta
import bcrypt
import secrets
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity, jwt_required,
    get_jwt, unset_jwt_cookies
) 
from app import mongo, jwt
from bson import ObjectId

import os

auth_bp = Blueprint('auth', __name__)
# import logging

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Token Blacklist
blacklisted_tokens = set()

 

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration with email verification."""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        # Check required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'phoneNumber', 'address']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'All fields are required'}), 400

        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'message': 'Invalid email format'}), 400

        # Validate password strength
        is_strong, message = validate_password(data['password'])
        if not is_strong:
            return jsonify({'message': message}), 400

        # Check if email already exists
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'message': 'Email already exists'}), 400

        # Generate verification token
        verification_token = secrets.token_hex(32)

        # Prepare user data
        user_data = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'email': data['email'],
            'password': bcrypt.generate_password_hash(data['password'].encode('utf-8')),
            'phoneNumber': data['phoneNumber'],
            'address': data['address'],
            'avatar': data.get('avatar', ''),  # Optional avatar URL
            'isVerified': False,
            'role': 'user',
            'verificationToken': verification_token,
            'createdAt': datetime.utcnow(),
            'lastLogin': None
        }

        # Extract email from user data
        email = user_data['email']

        # Initialize wallet balance
        mongo.db.wallet_balance.insert_one({"user_email": email, "balance": 0.0})

        # Initialize empty utility balance
        for utility in ["water", "gas", "energy"]:
            mongo.db.utilities_balance.insert_one({"user_email": email, "type": utility, "units": 0.0})

        # Insert user into database
        result = mongo.db.users.insert_one(user_data)
        
        # Generate verification URL
        verification_url = url_for(
            'verification.verify_email',
            token=verification_token,
            _external=True
        )

        # Send verification email
        try:
            send_verification_email(data['email'], verification_url)
            return jsonify({
                'message': 'Registration successful. Please check your email to verify your account.',
                'userId': str(result.inserted_id)
            }), 201
        except Exception as email_error:
            print(f"Email sending failed: {str(email_error)}")
            return jsonify({
                'message': 'Registration successful but verification email could not be sent. Please contact support.',
                'userId': str(result.inserted_id)
            }), 201

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'An error occurred during registration', 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ('email', 'password')):
            return jsonify({'message': 'Email and password are required'}), 400

        user = mongo.db.users.find_one({'email': data['email']})
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401

        stored_password = user['password']
        if not bcrypt.check_password_hash(stored_password, data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401

        if not user.get('isVerified', False):
            return jsonify({'message': 'Please verify your email before logging in'}), 401

        # Generate JWT tokens
        access_token = create_access_token(
            identity=user['email'],
            additional_claims={'role': user.get('role', 'user')},
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(identity=user['email'])

        # Retrieve existing refresh tokens (if any)
        refresh_tokens = user.get('refreshTokens', [])

        # Append new refresh token and keep only the latest 5
        refresh_tokens.append(refresh_token)
        refresh_tokens = refresh_tokens[-5:]  # Keep only the last 5 tokens

        # Update the user document
        mongo.db.users.update_one(
            {'_id': user['_id']}, 
            {'$set': {'refreshTokens': refresh_tokens, 'lastLogin': datetime.utcnow()}}
        )

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'email': user['email'],
                'firstName': user.get('firstName', ''),
                'lastName': user.get('lastName', ''),
                'avatar': user.get('avatar', ''),
                'role': user.get('role', 'user'),
                'lastLogin': user.get('lastLogin')
            }
        }), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred during login', 'error': str(e)}), 500



 
@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)  # Require refresh token for logout
def logout():
    try:
        jti = get_jwt()["jti"]  # Get JWT ID (Token Identifier)
        identity = get_jwt_identity()

        print(f"Removing refresh token: {jti}")  # Debugging

        # Remove token from refreshTokens array
        result = mongo.db.users.update_one(
            {'email': identity},
            {'$pull': {'refreshTokens': jti}}
        )

        if result.modified_count == 0:
            print(f"No matching token found for user: {identity}")

        response = jsonify({'message': 'Logged out successfully'})
        unset_jwt_cookies(response)
        return response, 200

    except Exception as e:
        return jsonify({'message': 'Logout failed', 'error': str(e)}), 500

#If still not working, try replacing get_jwt()["jti"] with get_jwt()["token"].
#mongo.db.users.update_one(
    # {'email': identity},
    # {'$set': {'refreshTokens': []}}  # 🔥 Clear all refresh tokens
# )

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=user_id, expires_delta=timedelta(hours=1))

         # Fetch current tokens
        user_id = mongo.db.users.find_one({'email': user_id})
        new_access_token = user_id.get('refreshTokens', [])
        # Keep only the last 5 tokens
        new_access_token.append(new_access_token)
        new_access_token = new_access_token[-5:]  

        mongo.db.users.update_one(
            {'email': user_id},
            {'$set': {'refreshTokens': new_access_token}}
        )
        return jsonify({'access_token': new_access_token}), 200
    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500

@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklisted_tokens
# Add a status check endpoint
@auth_bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    """Check authentication status and get user info."""
    try:
        current_user_id = get_jwt_identity()
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        
        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({
            'isAuthenticated': True,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'firstName': user.get('firstName', ''),
                'lastName': user.get('lastName', ''),
                'role': user.get('role', 'user')
            }
        }), 200

    except Exception as e:
        print(f"Status check error: {str(e)}")
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}! This is a protected route.'}), 200


# Default route
@auth_bp.route('/')
def home():
    return "Welcome to the Token Meter Recharge System!"

