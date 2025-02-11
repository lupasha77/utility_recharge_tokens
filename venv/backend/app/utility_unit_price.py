from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # Adjust connection if needed
db = client["token_meter_recharge"]  # Connect to the database

# Collection for utility prices
utility_prices = db["utility_unit_prices"]

# Define utility prices
utilities = [
    {"utility_type": "water", "price_per_unit": 1.50, "currency": "USD","unit type": "cubic meters", "last_updated": datetime.utcnow()},
    {"utility_type": "gas", "price_per_unit": 2.00, "currency": "USD", "unit type": "cubic meters", "last_updated": datetime.utcnow()},
    {"utility_type": "energy", "price_per_unit": 0.13, "currency": "USD", "unit type": "kWh", "last_updated": datetime.utcnow()},
]

# Insert or update prices
for utility in utilities:
    utility_prices.update_one(
        {"utility_type": utility["utility_type"]},  # Find by utility type
        {"$set": utility},  # Update existing or insert new
        upsert=True
    )

print("Utility prices updated successfully!")
