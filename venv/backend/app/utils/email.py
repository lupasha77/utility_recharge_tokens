# app/utils/email.py
from flask_mail import Message
from app import mail
import logging

def send_verification_email(to_email, verification_url):
    try:
        msg = Message(
            'Verify Your Email - Token Meter System',
            sender='no-reply@tokenmeter.com',
            recipients=[to_email],
            html=f"""
            <h2>Welcome to Token Meter System!</h2>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create this account, please ignore this email.</p>
            <p>Thank you!</p>
            <p>Best regards,</p>
            <p>Token Meter System Team</p>
            """
        )
        mail.send(msg)
        logging.info(f"Verification email sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send verification email to {to_email}: {str(e)}")
        raise

    # Utility token email 
def send_token_email(email, token_data):
    """Send utility token details to user"""
    try:
        msg = Message("Your Recharge Token",
                      sender="admin@tokenmeter.com",  # Replace with a valid sender email
                      recipients=[email])

        print("Sending email with data:", token_data)  # Log the token data to check it
        
        msg = Message(
            'Your Utility Token - Token Meter System',
            sender='no-reply@tokenmeter.com',
            recipients=[email],
            html=f"""
            <h2>Your Utility Token Has Been Generated</h2>
            <p>Please find your token details below:</p>
            <p><strong>Transaction Id:</strong> {token_data['transaction_id']}</p>  <!-- Changed this line -->
            <p><strong>Utility Type:</strong> {token_data['utilityType']}</p>  <!-- Changed this line -->
            <p><strong>Token:</strong> {token_data['rechargeToken']}</p>  <!-- Changed this line -->
            <p><strong>Units:</strong> {token_data['units']}</p>
            <p><strong>Amount:</strong> ${token_data['totalAmount']}</p>  <!-- Changed this line -->
            <p>Please keep this token safe and do not share it with anyone.</p>
            <p>Thank you for using Token Meter System!</p>
            <p>Best regards,</p>
            <p>Token Meter System Team</p>
            """
        )
        mail.send(msg)
        logging.info(f"Token email sent to {email}")
    except Exception as e:
        print(f"Failed to send token email to {email}: {str(e)}")  # Log the error to check it
        logging.error(f"Failed to send token email to {email}: {str(e)}")
        raise
