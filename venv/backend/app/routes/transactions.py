# # // app/routes/transactions.py

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import logging  
from app.services.user_service import UserService
from app.services.utility_service import UtilityService
from app.services.wallet_service import WalletService
from app.utils.statements_generator import StatementGenerator, UserProfile, AccountBalances
from flask import Blueprint, jsonify, request, send_file, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import mongo
import pandas as pd
from io import BytesIO
from math import ceil 
import pdfkit
from jinja2 import Template
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file, make_response 
import logging

# path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# Configure pdfkit
PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
# pdfkit.from_url("http://google.com", "out.pdf", configuration=PDF_CONFIG)
 
transactions_bp = Blueprint('transactions', __name__)
logger = logging.getLogger(__name__)

@transactions_bp.route('/view', methods=['GET'])
@jwt_required()
def fetch_transactions():
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        utility_type = request.args.get('utility_type')
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')  # default sort by created_at
        sort_order = request.args.get('sort_order', 'desc')  # default newest first
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        if not start_date or not end_date:
            return jsonify({"message": "Missing required parameters"}), 400
        
        # Convert string dates to datetime objects
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
        
        # Build query
        query = {
            "user_email": current_user,
            "created_at": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        }
        
        # Add optional filters
        if utility_type:
            query["utility_type"] = utility_type
        if status:
            query["status"] = status
            
        # Calculate pagination
        skip = (page - 1) * per_page
        
        # Get total count for pagination
        total_count = mongo.db.utility_recharge_tokens.count_documents(query)
        
        # Determine sort direction
        sort_direction = -1 if sort_order == 'desc' else 1
        
        # Fetch paginated and sorted transactions
        transactions = list(mongo.db.utility_recharge_tokens.find(query)
                          .sort(sort_by, sort_direction)
                          .skip(skip)
                          .limit(per_page))
        
        # Calculate aggregations
        aggregations = mongo.db.utility_recharge_tokens.aggregate([
            {"$match": query},
            {"$group": {
                "_id": "$utility_type",
                "total_units": {"$sum": "$units"},
                "total_amount": {"$sum": "$total_amount"},
                "count": {"$sum": 1}
            }}
        ])
        
        # Format transactions
        formatted_transactions = [{
            "id": str(t["_id"]),
            "transaction_id": t.get("transaction_id", ""),
            "date": t["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "utility_type": t["utility_type"],
            "recharge_token": t.get("recharge_token", ""),
            "units": float(t.get("units", 0)),
            "total_amount": float(t.get("total_amount", 0)),
            "payment_method": t.get("payment_method", ""),
            "status": t.get("status", "")
        } for t in transactions]
        
        # Format aggregations
        summary = {agg["_id"]: {
            "total_units": float(agg["total_units"]),
            "total_amount": float(agg["total_amount"]),
            "count": agg["count"]
        } for agg in aggregations}
        
        return jsonify({
            "transactions": formatted_transactions,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_pages": ceil(total_count / per_page),
                "total_records": total_count
            },
            "summary": summary,
            "query_info": {
                "start_date": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "user": current_user,
                "filters": {
                    "utility_type": utility_type,
                    "status": status
                }
            }
        }), 200
        
    except ValueError as ve:
        logger.error(f"Date parsing error: {str(ve)}")
        return jsonify({
            "message": "Invalid date format. Please use YYYY-MM-DD HH:MM:SS format",
            "error": str(ve)
        }), 400
        
    except Exception as e:
        logger.error(f"Failed to fetch transactions: {str(e)}")
        return jsonify({
            "message": "Failed to fetch transactions",
            "error": str(e)
        }), 500


# Configure pdfkit
# PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Error handling decorator
def handle_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}")
            return jsonify({
                "message": "Operation failed",
                "error": str(e)
            }), 500
    wrapper.__name__ = f.__name__
    return wrapper

@transactions_bp.route('/tokens/download', methods=['GET'])
@jwt_required()
@handle_errors
def download_transactions():

    current_user = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    format_type = request.args.get('format', 'csv').lower()
    
    if not start_date or not end_date:
        return jsonify({"message": "Missing date parameters"}), 400
        
    # Convert string dates to datetime objects
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    
    # Get user details
    user = mongo.db.users.find_one({"email": current_user})
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    # Fetch transactions
    transactions = get_transactions(current_user, start_datetime, end_datetime)
    if not transactions:
        return jsonify({"message": "No transactions found for the selected period"}), 404
        
    # Calculate summary
    summary = calculate_summary(transactions)
    
    # Format transactions
    formatted_transactions = format_transactions(transactions)

    # Generate appropriate response based on format type
    generators = {
        'csv': generate_csv,
        'xlsx': generate_excel,
        'pdf': generate_pdf
    }
    
    generator = generators.get(format_type)
    if not generator:
        return jsonify({"message": "Unsupported format"}), 400
        
    return generator(formatted_transactions, summary, user, start_datetime, end_datetime)

def get_transactions(user_email, start_datetime, end_datetime):
    """Fetch transactions from database"""
    query = {
        "user_email": user_email,
        "created_at": {
            "$gte": start_datetime,
            "$lte": end_datetime
        }
    }
    return list(mongo.db.utility_recharge_tokens.find(query).sort("created_at", 1))

def calculate_summary(transactions):
    """Calculate transaction summary"""
    summary = {}
    for t in transactions:
        utility = t['utility_type']
        if utility not in summary:
            summary[utility] = {
                'total_units': 0,
                'total_amount': 0,
                'count': 0
            }
        summary[utility]['total_units'] += float(t.get('units', 0))
        summary[utility]['total_amount'] += float(t.get('total_amount', 0))
        summary[utility]['count'] += 1
    return summary

def format_transactions(transactions):
    """Format transactions for report"""
    return [{
        'Transaction ID': t.get('transaction_id', ''),
        'Date': t['created_at'].strftime("%Y-%m-%d %H:%M:%S"),
        'Utility Type': t['utility_type'],
        'Units': float(t.get('units', 0)),
        'Amount': float(t.get('total_amount', 0)),
        'Payment Method': t.get('payment_method', ''),
        'Status': t.get('status', ''),
        'Recharge Token': t.get('recharge_token', '')
    } for t in transactions]

# The generate_csv, generate_excel, and generate_pdf functions remain the same as in your original code
def generate_csv(transactions, summary, user, start_date, end_date):
    output = BytesIO()
    
    # Write header information
    header_info = [
        f"Utility Transactions Report",
        f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        f"User: {user['firstName']} {user['lastName']}",
        f"Email: {user['email']}",
        "",
        "Summary:",
    ]
    
    # Write summary
    summary_rows = []
    for utility, data in summary.items():
        summary_rows.append(f"{utility},Total Units: {data['total_units']},Total Amount: ${data['total_amount']:.2f},Count: {data['count']}")
    
    # Combine all data
    all_rows = header_info + summary_rows + ["", "Transaction Details:"]
    
    # Convert transactions to DataFrame and write to CSV
    df = pd.DataFrame(transactions)
    
    # Write to output
    output.write('\n'.join(all_rows).encode('utf-8'))
    output.write(b'\n')
    df.to_csv(output, index=False, encoding='utf-8')
    
    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'transactions_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv'
    )

def generate_excel(transactions, summary, user, start_date, end_date):
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Create header format
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'left'
        })
        
        # Create Summary worksheet
        summary_df = pd.DataFrame([
            ['Report Period:', f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"],
            ['User:', f"{user['firstName']} {user['lastName']}"],
            ['Email:', user['email']],
            ['', ''],
            ['Summary:', '']
        ])
        
        summary_df.to_excel(writer, sheet_name='Summary', index=False, header=False)
        
        # Add summary table
        summary_data = []
        for utility, data in summary.items():
            summary_data.append([
                utility,
                data['total_units'],
                f"${data['total_amount']:.2f}",
                data['count']
            ])
        
        summary_cols = ['Utility Type', 'Total Units', 'Total Amount', 'Transaction Count']
        pd.DataFrame(summary_data, columns=summary_cols).to_excel(
            writer,
            sheet_name='Summary',
            startrow=6,
            index=False
        )
        
        # Create Transactions worksheet
        pd.DataFrame(transactions).to_excel(writer, sheet_name='Transactions', index=False)
        
        # Adjust column widths
        for worksheet in writer.sheets.values():
            worksheet.set_column(0, 10, 15)
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'transactions_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.xlsx'
    )

def generate_pdf(transactions, summary, user, start_date, end_date):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
        </style>
    </head>
    <body>
        <h1>Utility Transactions Report</h1>
        <p>For Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</p>
        <p>User: {user['firstName']} {user['lastName']} ({user['email']})</p>
        <p>User: {user['phoneNumber']}    </p>
        <p>User: {user['address']}    </p>
        <p>User: {user['_id']}    </p>

        <h2>Summary</h2>
        <table>
            <tr><th>Utility Type</th><th>Total Units</th><th>Total Amount</th><th>Count</th></tr>
    """

    for utility, data in summary.items():
        html_content += f"""
            <tr>
                <td>{utility}</td>
                <td>{data['total_units']}</td>
                <td>${data['total_amount']:.2f}</td>
                <td>{data['count']}</td>
            </tr>
        """

    html_content += """
        </table>
        <h2>Transaction Details</h2>
        <table>
            <tr><th>Transaction ID</th><th>Date</th><th>Utility Type</th><th>Units</th><th>Amount</th><th>Payment Method</th><th>Status</th><th>Recharge Token</th></tr>
    """

    for t in transactions:
        html_content += f"""
            <tr>
                <td>{t['Transaction ID']}</td>
                <td>{t['Date']}</td>
                <td>{t['Utility Type']}</td>
                <td>{t['Units']}</td>
                <td>${t['Amount']:.2f}</td>
                <td>{t['Payment Method']}</td>
                <td>{t['Status']}</td>
                <td>{t['Recharge Token']}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    output = BytesIO()

    try:
        # Generate PDF directly into BytesIO
        options = {
            'enable-local-file-access': '',  # Allow local file access
            'no-stop-slow-scripts': '',  # Prevent stopping scripts that take longer
            'disable-smart-shrinking': '',  # Fix rendering issues
            'quiet': ''  # Suppress logs
        }

        pdf_data = pdfkit.from_string(html_content, output_path=False, configuration=PDF_CONFIG, options=options)


        # Write the generated PDF to BytesIO
        output.write(pdf_data)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f'transactions_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'
        )

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return jsonify({"message": "PDF generation failed", "error": str(e)}), 500

