from datetime import datetime
from pymongo import MongoClient
import logging

class MeterTokenHandler:
    def __init__(self, mongo_uri="mongodb://localhost:27017/"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.token_meter_recharge  # Replace with your actual database name
        
    def validate_and_apply_token(self, meter_id, token, utility_type):
        """
        Validates a token and applies it to the meter if valid
        Returns (success, message, units)
        """
        try:
            # Find the token in the database
            token_record = self.db.utility_recharge_tokens.find_one({
                "recharge_token": token,
                "utility_type": utility_type,
                "status": "active"
            })
            
            if not token_record:
                return False, "Invalid or already used token", 0
            
            # Get user's current utility balance
            user_email = token_record["user_email"]
            utility_balance = self.db.utilities_balance.find_one({
                "user_email": user_email,
                "utility_type": utility_type
            })
            
            if not utility_balance:
                return False, "User utility balance not found", 0
            
            # Start a session for atomic operations
            with self.client.start_session() as session:
                with session.start_transaction():
                    # Update token status to inactive
                    self.db.utility_recharge_tokens.update_one(
                        {"recharge_token": token},
                        {
                            "$set": {
                                "status": "inactive",
                                "used_at": datetime.utcnow(),
                                "meter_id": meter_id
                            }
                        },
                        session=session
                    )
                    
                    # Update utilities balance
                    self.db.utilities_balance.update_one(
                        {
                            "user_email": user_email,
                            "utility_type": utility_type
                        },
                        {
                            "$inc": {"units": -token_record["units"]},
                            "$set": {"last_updated": datetime.utcnow()}
                        },
                        session=session
                    )
            
            return True, "Token applied successfully", token_record["units"]
            
        except Exception as e:
            logging.error(f"Token validation error: {str(e)}")
            return False, f"Error processing token: {str(e)}", 0
            
    def get_token_info(self, token):
        """
        Get information about a token without applying it
        """
        token_record = self.db.utility_recharge_tokens.find_one({
            "recharge_token": token
        })
        return token_record

class PrepaidMeterWithDB(): #PrepaidMeter
    def __init__(self, meter_id, utility_type, token_handler, initial_balance=0):
        super().__init__(meter_id, initial_balance)
        self.utility_type = utility_type
        self.token_handler = token_handler
    
    def apply_token(self, token):
        """Override apply_token to use database validation"""
        success, message, units = self.token_handler.validate_and_apply_token(
            self.meter_id, token, self.utility_type
        )
        
        if success:
            self.balance += units
            self.last_updated = datetime.now()
            self.status = "ACTIVE" if self.balance > 0 else "INACTIVE"
            return True, f"Token applied successfully. Added {units} units. New balance: {self.balance}"
        
        return False, message