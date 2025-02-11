# // backend/app/meter_simulator/database_handler.py
# database_handler.py
from pymongo import MongoClient
from datetime import datetime
import logging

class DatabaseHandler:
    def __init__(self, db_name='token_meter_recharge'):
        self.logger = logging.getLogger(__name__)
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client[db_name]
            # Test connection
            self.client.server_info()
            self.logger.info(f"Successfully connected to database: {db_name}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}", exc_info=True)
            raise

    def find_token(self, token, utility_type, user_email):
        """Find an active token for the specified user and utility"""
        try:
            self.logger.info(f"Searching for token: {token} for {utility_type}")
            utility_recharge_tokens = self.db['utility_recharge_tokens']
            token_record = utility_recharge_tokens.find_one({
                'recharge_token': token,
                'status': 'active',  # Only find active tokens
                'utility_type': utility_type,
                'user_email': user_email
            })
            
            if token_record:
                self.logger.info(f"Valid active token found: {token}")
            else:
                self.logger.warning(f"Token not found or not active: {token}")
            return token_record
        except Exception as e:
            self.logger.error(f"Token search error: {str(e)}", exc_info=True)
            raise

    def update_token_status(self, token_id):
        """Mark a token as used"""
        try:
            self.logger.info(f"Updating token status for ID: {token_id}")
            utility_recharge_tokens = self.db['utility_recharge_tokens']
            result = utility_recharge_tokens.update_one(
                {'_id': token_id},
                {
                    '$set': {
                        'status': 'used',
                        'used_at': datetime.now()
                    }
                }
            )
            if result.modified_count > 0:
                self.logger.info(f"Token status updated to 'used': {token_id}")
            else:
                self.logger.warning(f"Token status update failed: {token_id}")
            return result
        except Exception as e:
            self.logger.error(f"Token status update error: {str(e)}", exc_info=True)
            raise

    def get_utility_balance(self, user_email, utility_type):
        """Get the utility balance from MongoDB (not meter balance)"""
        try:
            self.logger.info(f"Fetching utility balance for {user_email}, {utility_type}")
            utilities_balance = self.db['utilities_balance']
            balance = utilities_balance.find_one({
                'user_email': user_email,
                'utility_type': utility_type
            })
            self.logger.info(f"Utility balance retrieved for {user_email}: {balance['units'] if balance else 0}")
            return balance
        except Exception as e:
            self.logger.error(f"Balance retrieval error: {str(e)}", exc_info=True)
            raise

    def authenticate_user(self, email):
        try:
            self.logger.info(f"Attempting to authenticate user: {email}")
            users = self.db['users']
            user = users.find_one({'email': email})
            if user:
                self.logger.info(f"User found: {email}")
                return user
            else:
                self.logger.warning(f"User not found: {email}")
                return None
        except Exception as e:
            self.logger.error(f"Authentication error for {email}: {str(e)}", exc_info=True)
            raise

    def update_balance(self, user_email, utility_type, units):
        try:
            self.logger.info(f"Updating balance for {user_email}, {utility_type}: {units}")
            utilities_balance = self.db['utilities_balance']
            result = utilities_balance.update_one(
                {'user_email': user_email, 'utility_type': utility_type},
                {'$inc': {'units': units}},
                upsert=True
            )
            self.logger.info(f"Balance updated successfully for {user_email}")
            return result
        except Exception as e:
            self.logger.error(f"Balance update error: {str(e)}", exc_info=True)
            raise

    def get_balance(self, user_email, utility_type):
        try:
            self.logger.info(f"Fetching balance for {user_email}, {utility_type}")
            utilities_balance = self.db['utilities_balance']
            balance = utilities_balance.find_one({
                'user_email': user_email,
                'utility_type': utility_type
            })
            self.logger.info(f"Balance retrieved for {user_email}: {balance['units'] if balance else 0}")
            return balance
        except Exception as e:
            self.logger.error(f"Balance retrieval error: {str(e)}", exc_info=True)
            raise