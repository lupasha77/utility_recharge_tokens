from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask_mail import Message
from app import mongo, mail
from app.utils.logger import logger
from app.utils.decorators import timing_decorator

# Define Blueprint
verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify-email/<token>', methods=['GET'])
@timing_decorator
def verify_email(token):
    """Handles email verification via token."""
    try:
        logger.debug(f"Received token for verification: {token}")

        user = mongo.db.users.find_one({'verificationToken': token})
        if not user:
            logger.warning("Invalid or expired token.")
            return jsonify({
                'message': 'Invalid or expired verification link.',
                'redirect': '/resend-verification'
            }), 400

        logger.info(f"User found for verification: {user['email']}")

        if user.get('isVerified'):
            logger.info("User already verified. Redirecting to login.")
            return redirect('/login')

        # Mark user as verified
        mongo.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'isVerified': True, 'verificationToken': None}}
        )
        logger.info(f"User {user['email']} successfully verified.")
        return redirect('/login')

    except Exception as e:
        logger.error(f"Error during email verification: {str(e)}")
        return jsonify({'message': 'An error occurred during verification', 'error': str(e)}), 500

@verification_bp.route('/resend-verification', methods=['POST'])
@timing_decorator
def resend_verification():
    """Handles resending of verification email."""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'message': 'Email is required'}), 400

        user = mongo.db.users.find_one({'email': email})
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if user.get('isVerified'):
            return jsonify({'message': 'User is already verified. Please log in.'}), 400

        # Generate a new verification token
        new_token = create_access_token(identity=email, expires_delta=timedelta(hours=24))
        mongo.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'verificationToken': new_token}}
        )

        logger.info(f"New verification token generated for {email}: {new_token}")

        # Send the verification email
        verification_url = url_for('verification.verify_email', token=new_token, _external=True)
        msg = Message(
            'Verify Your Email',
            sender='no-reply@tokenmeter.com',
            recipients=[email],
            body=f'Click the link to verify your email: {verification_url}'
        )
        mail.send(msg)

        logger.info(f"Verification email sent to {email}")

        return jsonify({'message': 'A new verification email has been sent. Please check your inbox.'}), 200

    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
