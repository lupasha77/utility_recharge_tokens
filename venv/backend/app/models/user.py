# app/models/user.py
from datetime import datetime
from app import mongo
import bcrypt
import secrets
from bson import ObjectId

class User:
    @staticmethod
    def create(first_name, last_name, email, password, phone_number, address, avatar=None):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        verification_token = secrets.token_hex(16)
        
        user = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': hashed_password.decode('utf-8'),
            'phoneNumber': phone_number,
            'address': address,
            'avatar': avatar,  # Store avatar filename or URL
            'isVerified': False,
            'verificationToken': verification_token,
            'createdAt': datetime.utcnow(),
            'role': 'user',
            'lastLogin': None,
            'tokens': []
        }
        
        result = mongo.db.users.insert_one(user)
        return str(result.inserted_id), verification_token

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def find_by_id(user_id):
        return mongo.db.users.find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def verify_password(user, password):
        if user:
            return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
        return False

    @staticmethod
    def verify_email(token):
        user = mongo.db.users.find_one({'verificationToken': token})
        if user:
            mongo.db.users.update_one(
                {'_id': user['_id']},
                {
                    '$set': {
                        'isVerified': True,
                        'verificationToken': None,
                        'emailVerifiedAt': datetime.utcnow()
                    }
                }
            )
            return True
        return False

    @staticmethod
    def update_last_login(user_id):
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'lastLogin': datetime.utcnow()}}
        )