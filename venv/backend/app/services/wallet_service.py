# services/wallet_service.py
from typing import Optional
from app import mongo

class WalletService:
    @staticmethod
    def get_balance(user_email: str) -> float:
        wallet = mongo.db.wallet_balance.find_one({'userEmail': user_email})
        return wallet['wallet-balance'] if wallet else 0