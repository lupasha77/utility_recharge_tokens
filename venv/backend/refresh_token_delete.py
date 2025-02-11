from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app import mongo

def refresh_token_delete():
    user_id = get_jwt_identity()
    mongo.db.users.update_one(  
        {'email': user_id},
        {'$set': {'refreshTokens': []}}  # Clear all refresh tokens
    )
    return jsonify({'message': 'Refresh tokens deleted successfully'}), 200