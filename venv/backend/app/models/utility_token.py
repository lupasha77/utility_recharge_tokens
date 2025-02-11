# app/models/utility_token.py
from datetime import datetime
from app import mongo

class UtilityToken:
    collection = mongo.db.utility_tokens
    
    @staticmethod
    def create(token_data):
        return UtilityToken.collection.insert_one(token_data)
    
    @staticmethod
    def find_by_user(user_id):
        return UtilityToken.collection.find({'user_id': user_id})
    
    @staticmethod
    def find_by_token(token):
        return UtilityToken.collection.find_one({'token': token})