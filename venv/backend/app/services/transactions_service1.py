# services/transaction_service1.py
from typing import Dict, List
from datetime import datetime
from app import mongo
from pymongo import DESCENDING

class TransactionService:
    @staticmethod
    def get_recent_transactions(user_id: str, limit: int = 20) -> List[Dict]:
        transactions = list(mongo.db.transactions.find(
            {"user_id": user_id}
        ).sort("date", DESCENDING).limit(limit))
        
        return [{
            "type": txn["type"],
            "units": txn["units"],
            "amount": txn["amount"],
            "date": txn["date"].strftime("%Y-%m-%d"),
            "token": txn.get("token")
        } for txn in transactions]

    @staticmethod
    def get_monthly_summary(user_id: str) -> Dict[str, float]:
        current_month = datetime.utcnow().strftime("%Y-%m")
        summary = list(mongo.db.transactions.aggregate([
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$regex": f"^{current_month}"}
                }
            },
            {
                "$group": {
                    "_id": "$type",
                    "total_spent": {"$sum": "$amount"}
                }
            }
        ]))
        
        return {entry["_id"]: entry["total_spent"] for entry in summary}