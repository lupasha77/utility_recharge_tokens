# app/models/api_token.py
# app/models/api_token.py
from datetime import datetime
from bson import ObjectId
import secrets
from app import mongo

class APIToken:
    @staticmethod
    def create(user_id, name, expires_at):
        try:
            token = {
                'user_id': ObjectId(user_id),
                'name': name,
                'token': secrets.token_urlsafe(32),
                'created_at': datetime.utcnow(),
                'expires_at': expires_at,
                'last_used': None,
                'is_active': True
            }
            
            # Debug print
            print("Token before insert:", token)
            
            result = mongo.db.api_tokens.insert_one(token)
            token['_id'] = result.inserted_id
            
            # Convert the token to a dictionary if it isn't already
            return dict(token)
            
        except Exception as e:
            print("Error in APIToken.create:", str(e))
            raise
    @staticmethod
    def get_user_tokens(user_id):
        return list(mongo.db.api_tokens.find({'user_id': ObjectId(user_id)}))

    @staticmethod
    def revoke_token(token_id, user_id):
        return mongo.db.api_tokens.update_one(
            {'_id': ObjectId(token_id), 'user_id': ObjectId(user_id)},
            {'$set': {'is_active': False}}
        )
# # app/models/api_token.py
# from datetime import datetime
# from config import mongo
# from bson import ObjectId
# import secrets

# class APIToken:
#     @staticmethod
#     def create(user_id, name, expires_at):
#         token = {
#             'user_id': ObjectId(user_id),
#             'name': name,
#             'token': secrets.token_urlsafe(32),
#             'created_at': datetime.utcnow(),
#             'expires_at': expires_at,
#             'last_used': None,
#             'is_active': True
#         }
#         result = mongo.db.api_tokens.insert_one(token)
#         token['_id'] = result.inserted_id
#         return token

#     @staticmethod
#     def get_user_tokens(user_id):
#         return list(mongo.db.api_tokens.find({'user_id': ObjectId(user_id)}))