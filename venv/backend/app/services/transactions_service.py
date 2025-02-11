from datetime import datetime, timedelta
from flask import jsonify, send_file
from app import mongo
from app.utils.utility_token_generator import generate_recharge_token
from app.utils.statements_generator import generate_csv_statement, generate_pdf_statement
import logging

def process_purchase_token(user_email, data):
    """Processes token purchase"""
    user = mongo.db.users.find_one({'email': user_email})
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    utility_type = data.get('utilityType')
    units = data.get('units')

    if utility_type not in ['water', 'energy', 'gas']:
        return jsonify({'success': False, 'message': 'Invalid utility type'}), 400

    if not isinstance(units, int) or units <= 0:
        return jsonify({'success': False, 'message': 'Invalid units provided'}), 400

    rates = {'water': 10, 'energy': 15, 'gas': 20}
    total_amount = units * rates[utility_type]
    recharge_token = generate_recharge_token()

    token_data = {
        'userEmail': user_email,
        'rechargeToken': recharge_token,
        'purchaseDate': datetime.now(),
        'status': 'active',
        'utilityType': utility_type,
        'units': units,
        'totalAmount': total_amount
    }

    try:
        result = mongo.db.utility_recharge_tokens.insert_one(token_data)
        if not result.acknowledged:
            return jsonify({'success': False, 'message': 'Database insert failed'}), 500

        return jsonify({'success': True, 'rechargeToken': recharge_token, 'totalAmount': total_amount}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to save token', 'error': str(e)}), 500

def fetch_account_statement(user_email):
    """Fetches user account statement"""
    try:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        transactions = list(mongo.db.utility_recharge_tokens.find({
            'userEmail': user_email,
            'purchaseDate': {'$gte': start_date, '$lte': end_date}
        }).sort('purchaseDate', -1))

        monthly_totals = {
            'water': {'purchased': 0, 'used': 0, 'remaining': 0, 'cost': 0},
            'energy': {'purchased': 0, 'used': 0, 'remaining': 0, 'cost': 0},
            'gas': {'purchased': 0, 'used': 0, 'remaining': 0, 'cost': 0}
        }

        for tx in transactions:
            utility_type = tx['utilityType']
            monthly_totals[utility_type]['purchased'] += tx['units']
            monthly_totals[utility_type]['cost'] += tx['totalAmount']
            if tx['status'] == 'used':
                monthly_totals[utility_type]['used'] += tx['units']
            else:
                monthly_totals[utility_type]['remaining'] += tx['units']

        return jsonify({
            'monthly_totals': monthly_totals,
            'transactions': transactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_transactions(user_email, start_date, end_date):
    """Fetches transaction history"""
    if not start_date or not end_date:
        return jsonify({'success': False, 'message': 'Start and end date required'}), 400

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        transactions = list(mongo.db.utility_recharge_tokens.find({
            'userEmail': user_email,
            'purchaseDate': {'$gte': start_date, '$lte': end_date}
        }).sort('purchaseDate', -1))

        return jsonify({'success': True, 'transactions': transactions}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def fetch_and_download_statement(user_email, start_date, end_date, file_format):
    """Generates and returns account statement in CSV or PDF"""
    if not start_date or not end_date:
        return jsonify({'success': False, 'message': 'Start and end date required'}), 400

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        transactions = list(mongo.db.utility_recharge_tokens.find({
            'userEmail': user_email,
            'purchaseDate': {'$gte': start_date, '$lte': end_date}
        }).sort('purchaseDate', -1))

        if file_format == 'csv':
            return generate_csv_statement(user_email, transactions, start_date)
        elif file_format == 'pdf':
            return generate_pdf_statement(user_email, transactions, start_date)
        else:
            return jsonify({'success': False, 'message': 'Invalid format'}), 400

    except Exception as e:
        logging.error(f"Error generating statement: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
