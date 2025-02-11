from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, List, Tuple
import pandas as pd
import os
import pdfkit
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from logging import getLogger
import logging
from io import BytesIO
from math import ceil
from app import mongo 
from io import BytesIO 
import sys

logger = logging.getLogger(__name__)

logger = getLogger(__name__)

wallets_transactions_bp = Blueprint('wallets_transactions', __name__)
PDF_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
OUTPUT_DIR = "/tmp"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class TransactionService:
    @staticmethod
    def format_transaction(transaction: Dict, payment_method: str) -> Dict:
        """Format a single transaction."""
        return {
            "id": str(transaction["_id"]),
            "date": transaction["date"].strftime("%Y-%m-%d %H:%M:%S"),
            "initial_balance": transaction.get("initial_balance"),
            "final_balance": transaction.get("final_balance"),
            "utility_type": transaction.get("utility_type", "N/A"),
            "recharge_token": transaction.get("recharge_token", ""),
            "units": float(transaction.get("units", 0)),
            "amount": float(transaction.get("amount", 0)),
            "transaction_type": transaction.get("transaction_type", ""),
            "status": transaction.get("status", ""),
            "payment_method": payment_method
        }

    @staticmethod
    def get_transactions(user_email: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch and format transactions for a user within a date range."""
        query = {
            "user_email": user_email,
            "date": {"$gte": start_date, "$lte": end_date}
        }

        # Fetch transactions from both collections
        wallet_transactions = list(mongo.db.wallet_transactions.find(query))
        direct_transactions = list(mongo.db.direct_payments.find(query)) 

        # Format transactions
        formatted_transactions = [
            TransactionService.format_transaction(t, "wallet") for t in wallet_transactions
        ] + [
            TransactionService.format_transaction(t, "direct_pay") for t in direct_transactions
        ]

        return sorted(formatted_transactions, key=lambda x: x["date"], reverse=True) 


class DocumentGenerator:
    
    @staticmethod
    def calculate_summary_metrics(transactions: List[Dict], user_email: str) -> Dict:
        """Calculate all summary metrics from transactions and database collections."""
        summary = {
            'water': {'total_purchased': 0, 'total_used': 0, 'remaining_units': 0},
            'energy': {'total_purchased': 0, 'total_used': 0, 'remaining_units': 0},
            'gas': {'total_purchased': 0, 'total_used': 0, 'remaining_units': 0},
            'financial': {
                'total_deposits': 0,
                'total_direct_purchases': 0,
                'wallet_balance': 0
            }
        }

        try:

            # Get wallet balance
            logging.info(f"Querying wallet balance for: {user_email}")

            wallet_data = mongo.db.wallet_balance.find_one({"user_email": user_email})
            logging.info(wallet_data)
            if wallet_data and 'balance' in wallet_data:
                summary['financial']['wallet_balance'] = float(wallet_data.get('balance', 0))
            else:
                logging.warning(f"No wallet balance found for email: {user_email}")

            # Calculate metrics from transactions
            for t in transactions:
                utility_type = t.get('utility_type', 'N/A')
                transaction_type = t.get('transaction_type', '')
                payment_method = t.get('payment_method', '')
                amount = float(t.get('amount', 0))
                units = float(t.get('units', 0))

                # Calculate total purchased units per utility type
                if transaction_type == 'purchase_utility' and utility_type in summary:
                    summary[utility_type]['total_purchased'] += units

                # Calculate total deposits
                if transaction_type == 'deposit':
                    summary['financial']['total_deposits'] += amount

                # Calculate total direct purchases
                if payment_method == 'direct_pay':
                    summary['financial']['total_direct_purchases'] += abs(amount)

            # Calculate total used units from utility_recharge_token collection
            for utility_type in ['water', 'energy', 'gas']:
                used_units = mongo.db.utility_recharge_tokens.aggregate([
                    {
                        "$match": {
                            "user_email": user_email,
                            "utility_type": utility_type,
                            "status": {"$in": [ "used"]} #"inactive",
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "total_used": {"$sum": "$units"}
                        }
                    }
                ])
                used_result = list(used_units)
                print("Used Units:", used_result)
                if used_result:
                    summary[utility_type]['total_used'] = float(used_result[0].get('total_used', 0))
                else:
                    logging.warning(f"No usage data found for utility type: {utility_type}")

                # Calculate current balance units
                summary[utility_type]['remaining_units'] = (
                    summary[utility_type]['total_purchased'] - 
                    summary[utility_type]['total_used']
                )

        except Exception as e:
            logging.error(f"Error calculating summary metrics: {str(e)}")
            raise

        return summary
    
    @staticmethod
    def format_transaction_row(t: Dict) -> Dict:
        """Format a transaction row with safe dictionary access."""
        return {
            'date': t.get('date', 'N/A'),
            'id': t.get('id', 'N/A'),
            'transaction_type': t.get('transaction_type', 'N/A'),
            'payment_method': t.get('payment_method', 'N/A'),
            'utility_type': t.get('utility_type', 'N/A'),
            'units': float(t.get('units', 0)),
            'initial_balance': float(t.get('initial_balance', 0)) if t.get('initial_balance') else 0,
            'amount': float(t.get('amount', 0)),
            'final_balance': float(t.get('final_balance', 0)) if t.get('final_balance') else 0,
            'recharge_token': t.get('recharge_token', 'N/A'),
            'status': t.get('status', 'N/A')
        }

    @staticmethod
    def generate_pdf(transactions: List[Dict], user: Dict, start_date: datetime, end_date: datetime):
        """Generate a PDF report with enhanced summary metrics."""
        summary = DocumentGenerator.calculate_summary_metrics(transactions, user.get('email', ''))
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ text-align: center; color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background-color: #34495e; color: white; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
             
            <h1>Utility Transactions Report</h1>
            <p>For Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</p>
            <p>User: {user.get('firstName', '')} {user.get('lastName', '')} ({user.get('email', '')})</p>
            <p>Phone: {user.get('phoneNumber', 'N/A')}</p>
            <p>Address: {user.get('address', 'N/A')}</p>
            
            <h2>Financial Summary</h2>
            <table>
                <tr>
                    <th>Wallet Balance</th>
                    <th>Total Deposits</th>
                    <th>Total Direct Purchases</th>
                </tr>
                <tr>
                    <td>${summary['financial']['wallet_balance']:.2f}</td>
                    <td>${summary['financial']['total_deposits']:.2f}</td>
                    <td>${summary['financial']['total_direct_purchases']:.2f}</td>
                </tr>
            </table>
           
            <h2>Utility Usage Summary</h2>
            <table>
                <tr>
                    <th>Utility Type</th>
                    <th>Total Purchased Units</th>
                    <th>Total Used Units</th>
                    <th>Current Balance Units</th>
                </tr>
        """
        for utility_type in ['water', 'energy', 'gas']:
            data = summary[utility_type]
            html_content += f"""
                <tr>
                    <td>{utility_type.title()}</td>
                    <td>{data['total_purchased']:.2f}</td>
                    <td>{data['total_used']:.2f}</td>
                    <td>{data['remaining_units']:.2f}</td>
                </tr>
            """

        html_content += """
            </table>
            <h2>Transaction Details</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Transaction ID</th>
                    <th>Transaction Type</th>
                    <th>Payment Method</th>
                    <th>Utility Type</th>
                    <th>Units</th>
                    <th>Initial Balance</th>
                    <th>Amount</th>
                    <th>Final Balance</th>
                    <th>Recharge Token</th>
                    <th>Status</th>
                </tr>
        """

        for t in transactions:
            formatted = DocumentGenerator.format_transaction_row(t)
            html_content += f"""
                <tr>
                    <td>{formatted['date']}</td>
                    <td>{formatted['id']}</td>
                    <td>{formatted['transaction_type']}</td>
                    <td>{formatted['payment_method']}</td>
                    <td>{formatted['utility_type']}</td>
                    <td>{formatted['units']:.2f}</td>
                    <td>${formatted['initial_balance']:.2f}</td>
                    <td>${(formatted['amount']):.2f}</td>
                    <td>${formatted['final_balance']:.2f}</td>
                    <td>{formatted['recharge_token']}</td>
                    <td>{formatted['status']}</td>
                </tr>
            """

        html_content += """
            </table>
        </body>
        </html>
        """
        
        # PDF generation
        try:
            pdf_data = pdfkit.from_string(html_content, output_path=False, configuration=PDF_CONFIG)
            output = BytesIO(pdf_data)
            output.seek(0)
            return output
        except Exception as e:
            logging.error(f"PDF generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_xlsx(transactions: List[Dict], user: Dict, start_date: datetime, end_date: datetime):
        """Generate an XLSX report with enhanced summary metrics."""
        summary = DocumentGenerator.calculate_summary_metrics(transactions, user.get('email', ''))
        wb = Workbook()
        ws = wb.active
        ws.title = "Transactions"

        # Styling
        header_font = Font(bold=True)
        header_fill = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")
        
        # User Information
        ws.append(["User Information"])
        ws.append([f"Name: {user.get('firstName', '')} {user.get('lastName', '')}"])
        ws.append([f"Email: {user.get('email', '')}"])
        ws.append([f"Phone: {user.get('phoneNumber', 'N/A')}"])
        ws.append([f"Address: {user.get('address', 'N/A')}"])
        ws.append([])

        # Financial Summary
        ws.append(["Financial Summary"])
        ws.append(["Wallet Balance", "Total Deposits", "Total Direct Purchases"])
        ws.append([
            summary['financial']['wallet_balance'],
            summary['financial']['total_deposits'],
            summary['financial']['total_direct_purchases']
        ])
        ws.append([])

        # Utility Usage Summary
        ws.append(["Utility Usage Summary"])
        ws.append(["Utility Type", "Total Purchased Units", "Total Used Units", "Current Balance Units"])
        for utility_type in ['water', 'energy', 'gas']:
            data = summary[utility_type]
            ws.append([
                utility_type.title(),
                data['total_purchased'],
                data['total_used'],
                data['remaining_units']
            ])
        ws.append([])

        # Transactions Section
        headers = [
            "Date", "Transaction ID", "Type", "Payment Method", 
            "Utility Type", "Units", "Initial Balance", "Amount",
            "Final Balance", "Token", "Status"
        ]
        ws.append(headers)
        
        # Apply header styling
        for cell in ws[ws.max_row]:
            cell.font = header_font
            cell.fill = header_fill

        # Add transaction data
        for t in transactions:
            formatted = DocumentGenerator.format_transaction_row(t)
            ws.append([
                formatted['date'],
                formatted['id'],
                formatted['transaction_type'],
                formatted['payment_method'],
                formatted['utility_type'],
                formatted['units'],
                formatted['initial_balance'],
                formatted['amount'],
                formatted['final_balance'],
                formatted['recharge_token'],
                formatted['status']
            ])

        # Adjust column widths
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

        # Get the user's Downloads folder dynamically
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads") 
                # if sys.platform == "darwin" else "C:\\Users\\{username}\\Downloads").format(username=os.environ.get('USERNAME'))
            base_name = "report"
            file_extension = ".xlsx"

            # ✅ Construct the correct file path
            counter = 1
            file_path = os.path.join(downloads_folder, f"{base_name}{file_extension}")

            # Generate unique filename: report.xlsx → report(1).xlsx → report(2).xlsx, etc.
            
            file_path = os.path.join(downloads_folder, f"{base_name}{file_extension}")
            counter = 1

            while os.path.exists(file_path):  # If file exists, add (1), (2), etc.
                file_path = os.path.join(downloads_folder, f"{base_name}({counter}){file_extension}")
                counter += 1

            try:
                # Save the Excel file
                wb.save(file_path)
                logging.info(f"Report saved successfully at: {file_path}")
                return file_path  # ✅ Return the file path for downloading

        
            except Exception as e:
                logging.error(f"Excel generation failed: {str(e)}")
                raise
@wallets_transactions_bp.route('/wallet-dir-pay-transactions/view', methods=['GET'])
@jwt_required()
def fetch_wallet_dir_pay_transactions():
    """Endpoint to fetch wallet and direct payment transactions."""
    try:
        current_user = get_jwt_identity()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"message": "Missing required parameters"}), 400

        start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)

        transactions = TransactionService.get_transactions(current_user, start_datetime, end_datetime)

        # Calculate summary metrics using the backend implementation
        summary_metrics = DocumentGenerator.calculate_summary_metrics(transactions, current_user)
        logging.info(summary_metrics)

        return jsonify({
            "transactions": transactions,
            "summary_metrics": summary_metrics,
            "query_info": {
                "start_date": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "user": current_user,
                "total_records": len(transactions)
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch transactions: {str(e)}")
        return jsonify({"message": "Failed to fetch transactions", "error": str(e)}), 500

@wallets_transactions_bp.route('/wallet-dir-pay-transactions/download', methods=['GET'])
@jwt_required()
def download_wallet_dir_pay_transactions():
    try:
        current_user = get_jwt_identity()
        start_date = datetime.strptime(request.args.get('start_date'), "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(request.args.get('end_date'), "%Y-%m-%d %H:%M:%S")
        format_type = request.args.get('format', 'csv').lower()

        # Get user data
        user_profile = mongo.db.users.find_one({"email": current_user})
        if not user_profile:
            return jsonify({"message": "User profile not found"}), 404

        # Get transactions
        transactions = TransactionService.get_transactions(current_user, start_date, end_date)
        if not transactions:
            return jsonify({"message": "No transactions found"}), 404

        # Set file path
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        file_name = f"transactions_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{format_type}"
        file_path = os.path.join(downloads_folder, file_name)

        if format_type == 'pdf':
            output = DocumentGenerator.generate_pdf(transactions, user_profile, start_date, end_date)
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=file_name
            )
        else:  # xlsx
            # DocumentGenerator.generate_xlsx(transactions, user_profile, start_date, end_date)

            # 🔥 Generate a uniquely named file to prevent overwriting
            file_path = DocumentGenerator.generate_xlsx(transactions, user_profile, start_date, end_date)

        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

    except Exception as e:
        logger.error(f"Failed to download transactions: {str(e)}")
        return jsonify({"message": "Failed to generate document", "error": str(e)}), 500

    