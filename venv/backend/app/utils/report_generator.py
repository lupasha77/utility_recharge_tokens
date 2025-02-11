# venv/backend/app/utils/report_generator.py
import io
import csv
from fpdf import FPDF
from flask import send_file


def generate_csv_statement(user_profile, balances, transactions, start_date):
    """Generates a CSV account statement"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write account holder details
    writer.writerow(["Account Holder Details"])
    writer.writerow(["First Name", user_profile.get("firstName", "N/A")])
    writer.writerow(["Last Name", user_profile.get("lastName", "N/A")])
    writer.writerow(["Email", user_profile.get("email", "N/A")])
    writer.writerow(["Phone", user_profile.get("phoneNumber", "N/A")])
    writer.writerow(["Address", user_profile.get("address", "N/A")])
    writer.writerow([])  # Blank line

    # Write account summary
    writer.writerow(["Account Summary"])
    writer.writerow(["Cash Balance", f"${balances['cash_balance']:.2f}"])
    writer.writerow(["Water Units", f"{balances['water_units']:.2f}"])
    writer.writerow(["Energy Units", f"{balances['energy_units']:.2f}"])
    writer.writerow(["Gas Units", f"{balances['gas_units']:.2f}"])
    writer.writerow([])  # Blank line

    # Write transactions
    writer.writerow(["Transaction History"])
    writer.writerow(["Date", "Utility Type", "Units", "Total Amount", "Status", "Recharge Token"])

    for tx in transactions:
        writer.writerow([
            tx['purchaseDate'].strftime('%Y-%m-%d %H:%M:%S'),
            tx['utilityType'],
            tx['units'],
            tx['totalAmount'],
            tx['status'],
            tx['rechargeToken']
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"account_statement_{start_date.strftime('%Y%m%d')}.csv"
    )


def generate_pdf_statement(user_profile, balances, transactions, start_date):
    """Generates a PDF account statement"""
    pdf = FPDF()
    pdf.add_page()

    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Account Statement", ln=True, align='C')
    pdf.ln(10)

    # Add account holder details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Account Holder Details", ln=True)
    pdf.set_font("Arial", size=10)

    pdf.cell(95, 8, "First Name:", 0)
    pdf.cell(95, 8, user_profile.get("firstName", "N/A"), 0, ln=True)

    pdf.cell(95, 8, "Last Name:", 0)
    pdf.cell(95, 8, user_profile.get("lastName", "N/A"), 0, ln=True)

    pdf.cell(95, 8, "Email:", 0)
    pdf.cell(95, 8, user_profile.get("email", "N/A"), 0, ln=True)

    pdf.cell(95, 8, "Phone:", 0)
    pdf.cell(95, 8, user_profile.get("phoneNumber", "N/A"), 0, ln=True)

    pdf.cell(95, 8, "Address:", 0)
    pdf.cell(95, 8, user_profile.get("address", "N/A"), 0, ln=True)

    pdf.ln(10)

    # Add account summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Account Summary", ln=True)
    pdf.set_font("Arial", size=10)

    pdf.cell(95, 8, "Cash Balance:", 0)
    pdf.cell(95, 8, f"${balances['cash_balance']:.2f}", 0, ln=True)

    pdf.cell(95, 8, "Water Units:", 0)
    pdf.cell(95, 8, f"{balances['water_units']:.2f}", 0, ln=True)

    pdf.cell(95, 8, "Energy Units:", 0)
    pdf.cell(95, 8, f"{balances['energy_units']:.2f}", 0, ln=True)

    pdf.cell(95, 8, "Gas Units:", 0)
    pdf.cell(95, 8, f"{balances['gas_units']:.2f}", 0, ln=True)

    pdf.ln(10)

    # Add transactions table
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Transaction History", ln=True)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 10, "Date", 1)
    pdf.cell(25, 10, "Utility", 1)
    pdf.cell(20, 10, "Units", 1)
    pdf.cell(25, 10, "Amount", 1)
    pdf.cell(25, 10, "Status", 1)
    pdf.cell(60, 10, "Token", 1, ln=True)

    pdf.set_font("Arial", size=10)
    for tx in transactions:
        pdf.cell(35, 10, tx['purchaseDate'].strftime('%Y-%m-%d'), 1)
        pdf.cell(25, 10, tx['utilityType'], 1)
        pdf.cell(20, 10, str(tx['units']), 1)
        pdf.cell(25, 10, f"${tx['totalAmount']}", 1)
        pdf.cell(25, 10, tx['status'], 1)
        pdf.cell(60, 10, tx['rechargeToken'], 1, ln=True)

    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"account_statement_{start_date.strftime('%Y%m%d')}.pdf"
    )
def get_account_balances(user_id):
    """Fetch account balances for the user"""
    # Replace with actual database query to fetch the user's balances
    # Example balances data, should come from a real database
    balances = {
        'cash_balance': 120.50,
        'water_units': 45.75,
        'energy_units': 150.30,
        'gas_units': 20.25
    }
    return balances


def format_transaction(transaction):
    """Formats a single transaction into a dictionary"""
    formatted_transaction = {
        'purchaseDate': transaction.get('purchaseDate'),
        'utilityType': transaction.get('utilityType'),
        'units': transaction.get('units'),
        'totalAmount': transaction.get('totalAmount'),
        'status': transaction.get('status'),
        'rechargeToken': transaction.get('rechargeToken')
    }
    return formatted_transaction
