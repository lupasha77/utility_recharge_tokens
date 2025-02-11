#  app/utils/statements_generator.py
from dataclasses import dataclass
from typing import Dict, List, DefaultDict, Optional
from datetime import datetime
import io
import csv
from collections import defaultdict
from fpdf import FPDF
from flask import send_file

@dataclass
class UserProfile:
    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        return cls(
            first_name=data.get('firstName', 'N/A'),
            last_name=data.get('lastName', 'N/A'),
            email=data.get('email', 'N/A'),
            phone_number=data.get('phoneNumber', 'N/A'),
            address=data.get('address', 'N/A')
        )

@dataclass
class AccountBalances:
    cash_balance: float
    water_units: float
    energy_units: float
    gas_units: float

    @classmethod
    def from_dict(cls, data: Dict) -> 'AccountBalances':
        return cls(
            cash_balance=data['cash_balance'],
            water_units=data['water_units'],
            energy_units=data['energy_units'],
            gas_units=data['gas_units']
        )

class StatementGenerator:
    UTILITY_TYPES = ['water', 'energy', 'gas']

    def __init__(self, user_profile: UserProfile, transactions: List[Dict], 
                 start_date: str, end_date: str, balances: Optional[AccountBalances] = None):
        self.user_profile = user_profile
        self.transactions = transactions
        self.start_date = start_date
        self.end_date = end_date
        self.balances = balances
        self.monthly_summary = self._calculate_monthly_summary()

    def _calculate_monthly_summary(self) -> DefaultDict:
        """Calculate monthly summaries for each utility type"""
        summary = defaultdict(lambda: defaultdict(lambda: {'units': 0, 'cost': 0}))
        
        for tx in self.transactions:
            month = tx['date'].strftime('%Y-%m')
            utility_type = tx['type']
            summary[month][utility_type]['units'] += tx['units']
            summary[month][utility_type]['cost'] += tx['amount']
        
        return summary

    def _write_user_details(self, writer) -> None:
        """Write user profile details to CSV"""
        writer.writerow(["Account Holder Details"])
        writer.writerow(["First Name", self.user_profile.first_name])
        writer.writerow(["Last Name", self.user_profile.last_name])
        writer.writerow(["Email", self.user_profile.email])
        writer.writerow(["Phone", self.user_profile.phone_number])
        writer.writerow(["Address", self.user_profile.address])
        writer.writerow([])

    def generate_csv_statement(self) -> send_file:
        """Generate CSV statement"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header section
        writer.writerow(['Account Statement'])
        self._write_user_details(writer)
        writer.writerow([f'Period: {self.start_date} to {self.end_date}'])
        writer.writerow([])
        
        # Monthly summary section
        writer.writerow(['Monthly Summary'])
        writer.writerow(['Month', 'Utility Type', 'Total Units', 'Total Cost'])
        
        for month in sorted(self.monthly_summary.keys()):
            for utility in self.UTILITY_TYPES:
                data = self.monthly_summary[month][utility]
                writer.writerow([
                    month,
                    utility,
                    data['units'],
                    f"${data['cost']:.2f}"
                ])
        
        writer.writerow([])
        
        # Transaction details section
        writer.writerow(['Transaction Details'])
        writer.writerow(['Date', 'Utility Type', 'Units', 'Amount', 'Status', 'Token'])
        
        for tx in self.transactions:
            writer.writerow([
                tx['date'].strftime('%Y-%m-%d %H:%M:%S'),
                tx['type'],
                tx['units'],
                f"${tx['amount']:.2f}",
                tx['status'],
                tx.get('recharge_token', 'N/A')
            ])
        
        output.seek(0)
        return self._create_file_response(output.getvalue().encode('utf-8'), 'text/csv')

    def generate_pdf_statement(self) -> send_file:
        """Generate PDF statement"""
        pdf = FPDF()
        pdf.add_page()
        
        self._add_pdf_header(pdf)
        self._add_pdf_account_details(pdf)
        if self.balances:
            self._add_pdf_account_summary(pdf)
        self._add_pdf_monthly_summary(pdf)
        self._add_pdf_transaction_details(pdf)
        
        return self._create_file_response(pdf.output(dest='S').encode('latin1'), 'application/pdf')

    def _add_pdf_header(self, pdf: FPDF) -> None:
        """Add header section to PDF"""
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "Account Statement", ln=True, align='C')
        pdf.ln(10)

    def _add_pdf_account_details(self, pdf: FPDF) -> None:
        """Add account holder details to PDF"""
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, "Account Holder Details", ln=True)
        pdf.set_font("Arial", size=10)

        details = [
            ("First Name:", self.user_profile.first_name),
            ("Last Name:", self.user_profile.last_name),
            ("Email:", self.user_profile.email),
            ("Phone:", self.user_profile.phone_number),
            ("Address:", self.user_profile.address)
        ]

        for label, value in details:
            pdf.cell(95, 8, label, 0)
            pdf.cell(95, 8, value, 0, ln=True)

        pdf.ln(10)

    def _add_pdf_account_summary(self, pdf: FPDF) -> None:
        """Add account summary section to PDF"""
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, "Account Summary", ln=True)
        pdf.set_font("Arial", size=10)

        summaries = [
            ("Cash Balance:", f"${self.balances.cash_balance:.2f}"),
            ("Water Units:", f"{self.balances.water_units:.2f}"),
            ("Energy Units:", f"{self.balances.energy_units:.2f}"),
            ("Gas Units:", f"{self.balances.gas_units:.2f}")
        ]

        for label, value in summaries:
            pdf.cell(95, 8, label, 0)
            pdf.cell(95, 8, value, 0, ln=True)

        pdf.ln(10)
        pdf.cell(190, 10, f'Period: {self.start_date} to {self.end_date}', ln=True)
        pdf.ln(10)

    def _add_pdf_monthly_summary(self, pdf: FPDF) -> None:
        """Add monthly summary section to PDF"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Monthly Summary', ln=True)
        
        # Table headers
        pdf.set_font('Arial', 'B', 10)
        headers = ['Month', 'Utility', 'Total Units', 'Total Cost']
        widths = [40, 30, 30, 30]
        
        for header, width in zip(headers, widths):
            pdf.cell(width, 10, header, 1)
        pdf.ln()
        
        # Table data
        pdf.set_font('Arial', '', 10)
        for month in sorted(self.monthly_summary.keys()):
            for utility in self.UTILITY_TYPES:
                data = self.monthly_summary[month][utility]
                pdf.cell(40, 10, month, 1)
                pdf.cell(30, 10, utility, 1)
                pdf.cell(30, 10, f"{data['units']:.2f}", 1)
                pdf.cell(30, 10, f"${data['cost']:.2f}", 1, ln=True)
        
        pdf.ln(10)

    def _add_pdf_transaction_details(self, pdf: FPDF) -> None:
        """Add transaction details section to PDF"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Transaction Details', ln=True)
        
        # Table headers
        headers = ['Date', 'Utility', 'Units', 'Amount', 'Status', 'Token']
        widths = [35, 25, 25, 25, 25, 55]
        
        pdf.set_font('Arial', 'B', 10)
        for header, width in zip(headers, widths):
            pdf.cell(width, 10, header, 1)
        pdf.ln()
        
        # Table data
        pdf.set_font('Arial', '', 10)
        for tx in self.transactions:
            row_data = [
                tx['date'].strftime('%Y-%m-%d'),
                tx['type'],
                f"{tx['units']:.2f}",
                f"${tx['amount']:.2f}",
                tx['status'],
                tx.get('recharge_token', 'N/A')
            ]
            
            for value, width in zip(row_data, widths):
                pdf.cell(width, 10, value, 1)
            pdf.ln()

    def _create_file_response(self, data: bytes, mimetype: str) -> send_file:
        """Create Flask file response"""
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'statement_{self.start_date}_{self.end_date}.{"csv" if mimetype == "text/csv" else "pdf"}'
        )

# Example usage in your routes:
def generate_statement(user_email, transactions, start_date, end_date, user_profile_data, format='pdf', balances=None):
    user_profile = UserProfile.from_dict(user_profile_data)
    account_balances = AccountBalances.from_dict(balances) if balances else None
    
    generator = StatementGenerator(
        user_profile=user_profile,
        transactions=transactions,
        start_date=start_date,
        end_date=end_date,
        balances=account_balances
    )
    
    return generator.generate_pdf_statement() if format == 'pdf' else generator.generate_csv_statement()