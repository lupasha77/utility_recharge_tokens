# // app/routes/wallet.py
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from app.services.wallet_service import WalletService
from app.utils.utility_token_generator import generate_recharge_token
from app.utils.email import send_token_email
from flask import Blueprint, jsonify, request, redirect, url_for
from datetime import datetime
from bson.objectid import ObjectId
from app import mongo  # Assuming MongoDB is initialized
import logging  
from app.services.utility_service import UtilityService 

wallet_bp = Blueprint('wallet', __name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Utility rates
utility_type = ["water","gas","energy"]  # Define a default utility type

# Fetch the unit price for the current utility type
unit_price = UtilityService.get_unit_price(utility_type)

# View wallet balance
@wallet_bp.route('/balances', methods=['GET'])
@jwt_required()
def get_wallet_balance():
    user_email = get_jwt_identity()

    try:
        balance = mongo.db.wallet_balance.find_one({"user_email": user_email})
        return jsonify({
            "wallet_balance": balance["balance"] if balance else 0.0
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'message': 'An error occurred',
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

# Deposit funds to wallet (Redirect to payments page)
from datetime import datetime
from bson.objectid import ObjectId

@wallet_bp.route('/deposit-funds', methods=['POST', 'OPTIONS'])
@jwt_required()
def deposit_funds():
    if request.method == "OPTIONS":  # Handle preflight request
        response = jsonify({'message': 'Preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    data = request.get_json()
    user_email = get_jwt_identity()

    if "amount" not in data or not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
        return jsonify({"message": "Invalid deposit amount"}), 400

    # Fetch the current wallet balance
    user_wallet = mongo.db.wallet_balance.find_one({"user_email": user_email})
    initial_balance = user_wallet["balance"] if user_wallet else 0  # Default to 0 if no wallet exists

    # New balance after deposit
    deposit_amount = float(data["amount"])
    final_balance = initial_balance + deposit_amount

    # Update wallet balance
    mongo.db.wallet_balance.update_one(
        {"user_email": user_email},
        {"$set": {"balance": final_balance}},
        upsert=True
    )

    # Create a unique transaction ID
    transaction_id = str(ObjectId())

    # Log transaction in `wallet_transactions`
    transaction = {
        "_id": transaction_id,
        "user_email": user_email,
        "transaction_type": "deposit",
        "amount": deposit_amount,
        "initial_balance": initial_balance,
        "final_balance": final_balance,
        "date": datetime.utcnow(),
        "status": "completed"
    }
    mongo.db.wallet_transactions.insert_one(transaction)

    return jsonify({
        "message": "Deposit successful",
        "transaction_id": transaction_id,
        "initial_balance": initial_balance,
        "deposited_amount": deposit_amount,
        "final_balance": final_balance
    }), 201

# // app/routes/wallet.py
# Purchase utility units (Redirect to payments page)
@wallet_bp.route('/purchase-utility', methods=['POST', 'OPTIONS'])
@jwt_required()
def purchase_utility():
    if request.method == "OPTIONS":
        response = jsonify({'message': 'Preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200

    data = request.get_json()
    user_email = get_jwt_identity()

    # Validate request data
    if "utility_type" not in data or "units" not in data or not isinstance(data["units"], int) or data["units"] <= 0:
        return jsonify({"message": "Invalid utility purchase request"}), 400

    utility_type = data["utility_type"]
    units_purchased = data["units"]
    payment_method = data.get("payment_method", "wallet")

    # Validate utility type
    unit_price = UtilityService.get_unit_price(utility_type)
    if not unit_price:
        return jsonify({"message": "Invalid utility type"}), 400

    cost = units_purchased * unit_price

    try:
        # Handle wallet payment logic
        if payment_method == "wallet":
            user_wallet = mongo.db.wallet_balance.find_one({"user_email": user_email})
            if not user_wallet:
                return jsonify({"message": "Wallet not found"}), 404
            
            wallet_balance = user_wallet["balance"]
            if wallet_balance < cost:
                return jsonify({
                    "message": "Insufficient balance in wallet. Would you like to pay directly?",
                    "required_amount": cost - wallet_balance,
                    "wallet_balance": wallet_balance,
                    "payment_options": ["Stripe", "Ecocash", "Omari", "OneMoney"]
                }), 402

            initial_balance = wallet_balance
            final_balance = initial_balance - cost
        else:
            initial_balance = None
            final_balance = None

        # Generate Recharge Token
        recharge_token = generate_recharge_token()
        if not recharge_token:
            return jsonify({"message": "Failed to generate recharge token"}), 500

        # Create a unique transaction ID
        transaction_id = str(ObjectId())

        # Start a session for atomic operations
        with mongo.db.client.start_session() as session:
            with session.start_transaction():
                # Update wallet balance if using wallet payment
                if payment_method == "wallet":
                    result = mongo.db.wallet_balance.update_one(
                        {"user_email": user_email},
                        {"$set": {"balance": final_balance}},
                        session=session
                    )
                    if result.modified_count == 0:
                        raise Exception("Failed to update wallet balance")

                # Update utilities balance with upsert
                update_result = mongo.db.utilities_balance.update_one(
                    {
                        "user_email": user_email,
                        "utility_type": utility_type
                    },
                    {
                        "$inc": {"units": units_purchased},
                        "$setOnInsert": {
                            "user_email": user_email,
                            "utility_type": utility_type,
                            "created_at": datetime.utcnow()
                        },
                        "$set": {"last_updated": datetime.utcnow()}
                    },
                    upsert=True,
                    session=session
                )
                
                if not (update_result.modified_count > 0 or update_result.upserted_id):
                    raise Exception("Failed to update utilities balance")

                # Store Recharge Token
                mongo.db.utility_recharge_tokens.insert_one({
                    "transaction_id": transaction_id,
                    "user_email": user_email,
                    "utility_type": utility_type,
                    "recharge_token": recharge_token,
                    "units": units_purchased,
                    "total_amount": cost,
                    "payment_method": payment_method,
                    "status": "active",
                    "created_at": datetime.utcnow()
                }, session=session)

                # Create transaction record
                transaction = {
                    "_id": transaction_id,
                    "user_email": user_email,
                    "transaction_type": "purchase_utility",
                    "amount": -cost if payment_method == "wallet" else cost,
                    "initial_balance": initial_balance,
                    "final_balance": final_balance,
                    "utility_type": utility_type,
                    "recharge_token": recharge_token,
                    "units": units_purchased,
                    "payment_method": payment_method,
                    "date": datetime.utcnow(),
                    "status": "completed"
                }

                # Store transaction in appropriate collection
                if payment_method == "wallet":
                    mongo.db.wallet_transactions.insert_one(transaction, session=session)
                else:
                    mongo.db.direct_payments.insert_one(transaction, session=session)

        # Send email after transaction is committed
        token_data = {
            'transaction_id': transaction_id,
            'utilityType': utility_type,
            'rechargeToken': recharge_token,
            'units': units_purchased,
            'totalAmount': cost,
            'newBalance': final_balance if payment_method == "wallet" else None,
            'paymentMethod': payment_method
        }

        try:
            send_token_email(user_email, token_data)
            print("Email sent successfully")
        except Exception as e:
            logging.error(f"Email sending failed: {str(e)}")
            # Continue even if email fails

        # Verify the utilities balance update
        updated_balance = mongo.db.utilities_balance.find_one({
            "user_email": user_email,
            "utility_type": utility_type
        })

        return jsonify({
            "message": "Utility purchase successful",
            "transaction_id": transaction_id,
            "payment_method": payment_method,
            "initial_balance": initial_balance,
            "deducted_amount": cost if payment_method == "wallet" else 0,
            "final_balance": final_balance,
            "recharge_token": recharge_token,
            "current_utility_balance": updated_balance["units"] if updated_balance else units_purchased
        }), 201

    except Exception as e:
        logging.error(f"Purchase utility error: {str(e)}")
        return jsonify({"message": "Transaction failed", "error": str(e)}), 500

# Get transaction history (Wallet Statement)
@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_wallet_transactions():
    user_email = get_jwt_identity()
    transactions = mongo.db.wallet_transactions.find({"user_email": user_email})

    return jsonify({
        "transactions": [{**t, "_id": str(t["_id"])} for t in transactions]
    }), HTTPStatus.OK
