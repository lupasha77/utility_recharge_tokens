# // backend/app/meter_simulator/meter_emulator.py
# meter_emulator.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from database_handler import DatabaseHandler
from keypad_widget import KeypadWidget
from utils import format_token
import logging
from datetime import datetime
import random
import requests
import json

class MeterEmulator(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_logging()
        self.init_database()
        self.current_user = None
        self.meter_balance = {'water': 0.0, 'gas': 0.0, 'energy': 0.0}
        self.usage_rate = {'water':0.2, 'gas': 0.2, 'energy': 0.3}
        self.backend_url = 'http://localhost:5000'  # Update with your backend URL
        self.usage_timer = QTimer()
        self.usage_timer.timeout.connect(self.simulate_usage)
        self.usage_timer.start(30000)  # Update every 1/2 minute
        self.initUI()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("prepaid_meter_emulator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Meter Emulator application starting...")

    def init_database(self):
        try:
            self.db_handler = DatabaseHandler()
            self.logger.info("Database connection established successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection: {str(e)}", exc_info=True)
            QMessageBox.critical(self, 'Database Error', 
                               'Failed to connect to database. Please check your connection.')

    def initUI(self):
        self.setWindowTitle('Prepaid Meter Emulator')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Left side - Controls
        self.auth_label = QLabel('User Authentication')
        self.auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.auth_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Enter your email')
        left_layout.addWidget(self.email_input)

        self.auth_button = QPushButton('Authenticate')
        self.auth_button.clicked.connect(self.authenticate_user)
        left_layout.addWidget(self.auth_button)

        self.utility_label = QLabel('Select Utility Type:')
        left_layout.addWidget(self.utility_label)

        self.utility_combo = QComboBox()
        self.utility_combo.addItems(['water', 'gas', 'energy'])
        self.utility_combo.currentTextChanged.connect(self.update_balance_display)
        left_layout.addWidget(self.utility_combo)

        self.token_label = QLabel('Enter 16-digit Token:')
        left_layout.addWidget(self.token_label)

        # Modified token input to allow mouse interaction
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('XXXX-XXXX-XXXX-XXXX')
        self.token_input.setReadOnly(False)  # Allow direct input
        self.token_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable focus for mouse clicks
        self.token_input.mousePressEvent = lambda _: self.token_input.setReadOnly(False)
        left_layout.addWidget(self.token_input)

        # Digital Display
        self.digital_display = QLabel('0.00')
        self.digital_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.digital_display.setFont(QFont('Arial', 48))
        self.digital_display.setStyleSheet("""
            QLabel {
                background-color: black;
                color: green;
                border: 2px solid gray;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        left_layout.addWidget(self.digital_display)

        # Right side - Keypad
        right_layout.addWidget(QLabel('Token Entry Keypad'))
        self.keypad = KeypadWidget(self.token_input)
        right_layout.addLayout(self.keypad)

        self.validate_button = QPushButton('Validate Token')
        self.validate_button.clicked.connect(self.validate_token)
        right_layout.addWidget(self.validate_button)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def authenticate_user(self):
        email = self.email_input.text().strip()
        self.logger.info(f"Attempting authentication for email: {email}")

        if not email:
            self.logger.warning("Authentication attempted with empty email")
            QMessageBox.warning(self, 'Authentication Failed', 'Please enter your email.')
            return

        try:
            user = self.db_handler.authenticate_user(email)
            if user:
                self.logger.info(f"Authentication successful for user: {email}")
                self.current_user = user
                QMessageBox.information(self, 'Authentication Successful', f'Welcome, {user["email"]}!')
                self.update_balance_display()
            else:
                self.logger.warning(f"Authentication failed - user not found: {email}")
                QMessageBox.warning(self, 'Authentication Failed', 'User not found.')
        except Exception as e:
            self.logger.error(f"Authentication error for {email}: {str(e)}", exc_info=True)
            QMessageBox.critical(self, 'Authentication Error', 
                               'An error occurred during authentication. Please try again.')

    def validate_token(self):
        if not self.current_user:
            self.logger.warning("Token validation attempted without user authentication")
            QMessageBox.warning(self, 'Authentication Required', 'Please authenticate first.')
            return

        raw_token = self.token_input.text().strip()
        self.logger.info(f"Token validation attempt - Raw token: {raw_token}")

        try:
            formatted_token = format_token(raw_token)
            if not formatted_token:
                self.logger.warning(f"Invalid token format: {raw_token}")
                QMessageBox.warning(self, 'Invalid Token', 
                                  'Please enter a valid 16-digit token in the format XXXX-XXXX-XXXX-XXXX.')
                return

            utility_type = self.utility_combo.currentText()
            token_record = self.db_handler.find_token(formatted_token, utility_type, self.current_user['email'])

            if token_record and token_record['status'] == 'active':
                self.logger.info(f"Valid token found: {formatted_token}")
                
                try:
                    # Add token units to meter balance
                    self.meter_balance[utility_type] += token_record['units']
                    
                    # Send recharge request to backend
                    recharge_data = {
                        'user_email': self.current_user['email'],
                        'utility_type': utility_type,
                        'token': formatted_token,
                        'units': token_record['units'],
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    response = requests.post(
                        f'{self.backend_url}/api/utilities/process-meter-recharge',
                        json=recharge_data
                    )
                    
                    if response.status_code == 200:
                        # Update token status to used
                        self.db_handler.update_token_status(token_record['_id'])
                        
                        self.logger.info(f"Recharge successful - Added {token_record['units']} units to meter balance")
                        self.update_balance_display()
                        self.token_input.clear()
                        
                        QMessageBox.information(
                            self, 
                            'Recharge Successful', 
                            f'Successfully added {token_record["units"]} units to your meter.\n'
                            f'Current meter balance: {self.meter_balance[utility_type]:.2f} units'
                        )
                    else:
                        raise Exception(f"Backend recharge failed: {response.text}")
                    
                except requests.RequestException as e:
                    self.logger.error(f"Backend communication error: {str(e)}", exc_info=True)
                    QMessageBox.critical(self, 'Recharge Error', 
                                      'Failed to communicate with backend server. Please try again.')
                except Exception as e:
                    self.logger.error(f"Error during recharge process: {str(e)}", exc_info=True)
                    QMessageBox.critical(self, 'Recharge Error', 
                                      'An error occurred during the recharge process. Please try again.')
            else:
                self.logger.warning(f"Invalid or used token attempt: {formatted_token}")
                QMessageBox.warning(self, 'Invalid Token', 'This token is invalid or has already been used.')

        except Exception as e:
            self.logger.error(f"Token validation error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, 'Error', 'An error occurred during token validation.')
    
    def update_balance_display(self):
        """Update the display with current meter balance"""
        try:
            utility_type = self.utility_combo.currentText()
            self.digital_display.setText(f'{self.meter_balance[utility_type]:.2f}')
            self.logger.info(f"Display updated - Meter balance for {utility_type}: {self.meter_balance[utility_type]:.2f}")
        except Exception as e:
            self.logger.error(f"Error updating balance display: {str(e)}", exc_info=True)
            self.digital_display.setText('Error')

    def simulate_usage(self):
        """Simulate utility usage from meter balance"""
        if not self.current_user:
            return

        try:
            utility_type = self.utility_combo.currentText()
            current_balance = self.meter_balance[utility_type]

            if current_balance > 0:
                base_rate = self.usage_rate[utility_type]
                variation = random.uniform(-0.2, 0.2)
                actual_usage = max(0, base_rate * (1 + variation))
                
                # Deduct usage from meter balance
                self.meter_balance[utility_type] = max(0, current_balance - actual_usage)
                
                self.update_balance_display()
                self.logger.info(f"Usage simulation: {utility_type} consumed {actual_usage:.3f} units")

                if self.meter_balance[utility_type] < 10:
                    self.logger.warning(f"Low balance alert: {utility_type} meter balance at {self.meter_balance[utility_type]:.2f}")
                    QMessageBox.warning(self, 'Low Balance Alert', 
                                      f'Your {utility_type} meter balance is low: {self.meter_balance[utility_type]:.2f} units')

        except Exception as e:
            self.logger.error(f"Usage simulation error: {str(e)}", exc_info=True)
        if not self.current_user:
            return

        try:
            utility_type = self.utility_combo.currentText()
            balance_record = self.db_handler.get_balance(self.current_user['email'], utility_type)

            if balance_record and balance_record.get('units', 0) > 0:
                base_rate = self.usage_rate[utility_type]
                variation = random.uniform(-0.2, 0.2)
                actual_usage = max(0, base_rate * (1 + variation))
                new_balance = max(0, balance_record.get('units', 0) - actual_usage)

                self.db_handler.update_balance(self.current_user['email'], utility_type, -actual_usage)
                self.update_balance_display()

                self.logger.info(f"Usage simulation: {utility_type} consumed {actual_usage:.3f} units")

                if new_balance < 10:
                    self.logger.warning(f"Low balance alert: {utility_type} balance at {new_balance:.2f}")
                    QMessageBox.warning(self, 'Low Balance Alert', 
                                      f'Your {utility_type} balance is low: {new_balance:.2f} units')

        except Exception as e:
            self.logger.error(f"Usage simulation error: {str(e)}", exc_info=True)