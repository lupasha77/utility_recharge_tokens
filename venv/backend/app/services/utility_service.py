# services/utility_service.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from app import mongo
from pymongo import DESCENDING
import logging
from http import HTTPStatus
# Set up logging
logging.basicConfig(level=logging.DEBUG)

@dataclass
class UtilityStats:
    type: str
    purchased: float
    purchased_cost: float
    used: float
    used_cost: float
    balance: float
    balance_cost: float

    @classmethod
    def calculate(cls, utility_type: str, purchases: List[Dict], usage: List[Dict]) -> 'UtilityStats':
        total_purchased = sum(txn["units"] for txn in purchases)
        total_purchased_cost = sum(txn["amount"] for txn in purchases)
        total_used = sum(usg["units"] for usg in usage)
        total_used_cost = sum(usg["cost"] for usg in usage)
        
        return cls(
            type=utility_type,
            purchased=total_purchased,
            purchased_cost=total_purchased_cost,
            used=total_used,
            used_cost=total_used_cost,
            balance=total_purchased - total_used,
            balance_cost=total_purchased_cost - total_used_cost
        )

@dataclass
class UtilityBalance:
    utility_type: str
    total: float
    used: float
    purchased: float
    cost: float
    remaining_units: float
    remaining_cost: float

    @classmethod
    def from_db(cls, data):
        return cls(
            utility_type=data.get('utility_type', ''),
            total=data.get('units', 0),  # Ensure correct key
            used=data.get('used', 0),  # Add missing fields if necessary
            purchased=data.get('purchased', 0),
            cost=data.get('cost', 0),
            remaining_units=data.get('remaining_units', 0),
            remaining_cost=data.get('remaining_cost', 0)
        )


class UtilityService:
    UTILITY_TYPES = ['water', 'energy', 'gas']

    @classmethod
    def get_unit_price(cls, utility_type: str) -> float:
        """Fetch unit price for a given utility type from MongoDB."""
        price_record = mongo.db.utility_unit_prices.find_one({"utility_type": utility_type})
        return price_record["price_per_unit"] if price_record else 0

    @classmethod
    def get_utility_stats(cls, user_id: str) -> List[UtilityStats]:
        stats = []
        for utility in cls.UTILITY_TYPES:
            purchases = list(mongo.db.transactions.find(
                {"user_id": user_id, "type": utility}
            ))
            usage = list(mongo.db.usage.find(
                {"user_id": user_id, "type": utility}
            ))
            stats.append(UtilityStats.calculate(utility, purchases, usage))
        return stats

    @classmethod
    def get_utility_balances(cls, user_email: str) -> List[UtilityBalance]:
        stats = list(mongo.db.utilities_balance.find({'userEmail': user_email}))  # Fetch all utilities

        if not stats:
            return [UtilityBalance(utility_type=t, total=0, used=0, purchased=0, 
                                cost=0, remaining_units=0, remaining_cost=0)
                    for t in cls.UTILITY_TYPES]

        # Create a dictionary to map utilities
        utility_map = {stat['utility_type']: stat for stat in stats}

        return [
            UtilityBalance.from_db(utility_map[t]) if t in utility_map else UtilityBalance(utility_type=t, total=0, used=0, purchased=0, cost=0, remaining_units=0, remaining_cost=0)
            for t in cls.UTILITY_TYPES
        ]

    from typing import List, Dict

 

    @classmethod
    def get_all_utility_balances(cls, user_email: str) -> List[Dict[str, float]]:
        # Fetch the latest balance for each utility type
        balances = list(mongo.db.utilities_balance.find({'user_email': user_email}))
        
        # Debugging logs
        print("User email:", user_email)
        print("Raw Balance Data:", balances)

        # Create a mapping of utility types to their latest balance
        utility_map = {b['utility_type']: b for b in balances}

        # Construct response ensuring all utility types are included
        return [
            {
                "utility_type": utility_type,
                "units": utility_map.get(utility_type, {}).get("units", 0)
            }
            for utility_type in cls.UTILITY_TYPES
        ]


    class UtilityService:
        UTILITY_TYPES = ['water', 'energy', 'gas']

    @classmethod
    def get_specific_utility_balance(cls, user_email: str, utility_type: str) -> Optional[float]:
        if utility_type not in cls.UTILITY_TYPES:
            return None

        # Find the latest balance data for the specific utility
        balance_data = mongo.db.utilities_balance.find_one(
            {'user_email': user_email, 'utility_type': utility_type},
            sort=[('last_updated', -1)]  # Sort by last_updated in descending order
        )

        # Debugging logs
        print("User email:", user_email)
        print("Balance Data:", balance_data)

        if balance_data:
            print("Extracted Units:", balance_data.get('units', 0))  # Debugging output

        # Return the balance if it exists, or 0 if not
        return balance_data.get('units', 0) if balance_data else 0

    @classmethod
    def add_utility_units(cls, user_email: str, utility_type: str, units: float, amount: float) -> float:
        if utility_type not in cls.UTILITY_TYPES:
            return None

        existing_balance = mongo.db.utility_balances.find_one({'userEmail': user_email}) or {}

        new_balance = existing_balance.get(utility_type, 0) + units
        total_cost = existing_balance.get(f"{utility_type}_cost", 0) + amount

        mongo.db.utility_balances.update_one(
            {'userEmail': user_email},
            {'$set': {utility_type: new_balance, f"{utility_type}_cost": total_cost}},
            upsert=True
        )

        return new_balance

    @classmethod
    def deduct_utility_units(cls, user_email: str, utility_type: str, units: float) -> Optional[float]:
        if utility_type not in cls.UTILITY_TYPES:
            return None

        balance_data = mongo.db.utility_balances.find_one({'userEmail': user_email})
        if not balance_data or balance_data.get(utility_type, 0) < units:
            return None  # Insufficient balance

        new_balance = balance_data[utility_type] - units

        mongo.db.utility_balances.update_one(
            {'userEmail': user_email},
            {'$set': {utility_type: new_balance}}
        )

        return new_balance

    @classmethod
    def get_utility_transactions(cls, user_email: str) -> List[Dict]:
        transactions = mongo.db.transactions.find({'user_email': user_email}).sort("date", DESCENDING)
        return [{**txn, '_id': str(txn['_id'])} for txn in transactions]

    @classmethod
    def get_monthly_utility_data(cls, user_email: str) -> List[Dict]:
        print("User Email:", user_email)
        current_date = datetime.utcnow()
        first_day_of_month = datetime(current_date.year, current_date.month, 1)
        last_month = first_day_of_month - timedelta(days=1)
        first_day_of_last_month = datetime(last_month.year, last_month.month, 1)

        # Get utilities for the current month
        utilities_data = list(mongo.db.utilities_balance.find({"user_email": user_email}))
        # Filter records for the current month and valid units (greater than 0)
        filtered_utilities = [
            utility for utility in utilities_data
            if utility.get('last_updated') and utility['last_updated'].month == current_date.month
            and utility['last_updated'].year == current_date.year
            and utility['units'] > 0
        ]

        # Print filtered utilities
        for utility in filtered_utilities:
            print("utility", utility)

        if not utilities_data:
            print("no utility data")
            # logging.warning(f"No utilities found for user: {user_email}")

        response_data = []

        for utility in utilities_data:
            utility_type = utility.get("utility_type") or utility.get("type")  # Handle both cases
            if not utility_type:
                # logging.warning(f"Skipping utility with missing type field: {utility}")
                continue  # Skip invalid records 

            # Get last month's balance
            last_month_record = mongo.db.utility_recharge_tokens.find_one({
                "userEmail": user_email,
                "utility_type": utility_type,
                "created_at": {"$gte": first_day_of_last_month, "$lt": first_day_of_month}
            })
            # logging.debug(f"Last month record: {last_month_record}")
            units_balance_brought_forward = last_month_record["units"] if last_month_record else 0
            # logging.debug(f"Balance brought forward for {utility_type}: {units_balance_brought_forward}")

            # Get units purchased this month
            purchases = list(mongo.db.utility_recharge_tokens.find({
                "user_email": user_email,
                "utility_type": utility_type,
                "created_at": {"$gte": first_day_of_month}
            }))
            # logging.debug(f"Purchases this month: {purchases}")

            units_purchased_to_date = sum(p["units"] for p in purchases)
            cost_of_units_purchased_to_date = sum(p["total_amount"] for p in purchases)

            # logging.debug(f"Units bought this month for {utility_type}: {units_purchased_to_date}, Cost: {cost_of_units_purchased_to_date}")

            # Get usage data (non-active tokens are considered used)
            used_records = list(mongo.db.utility_recharge_tokens.find({
                "user_email": user_email,
                "utility_type": utility_type,
                "status": {"$ne": "active"},
                "created_at": {"$gte": first_day_of_month}
            }))
            # print("used records", used_records)
            # logging.debug(f"Used records this month: {used_records}")

            units_used_to_date = sum(u["units"] for u in used_records)
            cost_of_units_used_to_date = sum(u["total_amount"] for u in used_records)
            # logging.debug(f"Units used this month for {utility_type}: {units_used_to_date}, Cost: {cost_of_units_used_to_date}")

            # Compute remaining balance
            # Fetch the unit price for the current utility type
            unit_price = cls.get_unit_price(utility_type)
            total_units_to_date=units_purchased_to_date+units_balance_brought_forward
            total_costs_to_date = total_units_to_date * unit_price  # This calculates the cost for the units bought

            units_balance_remaining_to_date = units_balance_brought_forward + units_purchased_to_date - units_used_to_date
            # logging.debug(f"Balance remaining for {utility_type}: {units_balance_remaining_to_date}")


            # Calculate the cost based on units and the fetched unit price

            response_data.append({
                "utility_type": utility_type,
                "units_balance_brought_forward": units_balance_brought_forward,
                "units_purchased_to_date": units_purchased_to_date,
                "units_used_to_date": units_used_to_date,
                "cost_of_units_used_to_date": cost_of_units_used_to_date,
                "cost_of_units_purchased_to_date": cost_of_units_purchased_to_date,
                "units_balance_remaining_to_date": units_balance_remaining_to_date,
                "unit_price": unit_price,  # Include the unit price in the response
                "total_costs_to_date": total_costs_to_date,  # total costs of units brought forward and purchased units to date  based on unit price
                "total_units_to_date": total_units_to_date
            })

        return response_data