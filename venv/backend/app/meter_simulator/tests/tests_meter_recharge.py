# // backend/app/meter_simulator/tests_meter_recharge.py
from flask.testing import FlaskClient
import pytest
from datetime import datetime
import requests
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app import create_app, mongo
 


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestMeterRecharge:
    @classmethod
    def setup_class(cls):
        """Set up test environment before all tests"""
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.base_url = 'http://localhost:5000/api/utilities'
        
        # Test data
        cls.test_user = {
            'email': 'leonard1@gmail.com',
            'utility_type': 'water'
        }
        
        # Ensure test user has a balance record
        with cls.app.app_context():
            cls.ensure_user_balance_exists()

    @classmethod
    def ensure_user_balance_exists(cls):
        """Initialize or verify user balance record exists"""
        utilities_balance = mongo.db.utilities_balance
        balance = utilities_balance.find_one({
            'user_email': cls.test_user['email'],
            'utility_type': cls.test_user['utility_type']
        })
        
        if not balance:
            logger.info("Creating new balance record for test user")
            utilities_balance.insert_one({
                'user_email': cls.test_user['email'],
                'utility_type': cls.test_user['utility_type'],
                'units': 0,
                'recharge_history': [],
                'last_updated': datetime.utcnow()
            })

    def test_valid_recharge(self):
        """Test successful meter recharge with valid token"""
        test_data = {
            'user_email': self.test_user['email'],
            'utility_type': self.test_user['utility_type'],
            'token': '8604-9933-2693-8672',
            'units': 13,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Testing recharge with data: {test_data}")
        
        response = requests.post(
            f'{self.base_url}/process-meter-recharge',
            json=test_data
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        assert response.json()['message'] == 'Recharge processed successfully'
        assert response.json()['units_deducted'] == test_data['units']

    def test_invalid_token_format(self):
        """Test recharge with invalid token format"""
        test_data = {
            'user_email': self.test_user['email'],
            'utility_type': self.test_user['utility_type'],
            'token': 'invalid-token',
            'units': 13,
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(
            f'{self.base_url}/process-meter-recharge',
            json=test_data
        )
        
        assert response.status_code == 400

    def test_missing_fields(self):
        """Test recharge with missing required fields"""
        test_data = {
            'user_email': self.test_user['email'],
            'utility_type': self.test_user['utility_type']
            # Missing token, units, and timestamp
        }
        
        response = requests.post(
            f'{self.base_url}/process-meter-recharge',
            json=test_data
        )
        
        assert response.status_code == 400
        assert 'Missing required fields' in response.json()['error']

    def verify_balance_update(self):
        """Verify that the balance was correctly updated in the database"""
        with self.app.app_context():
            utilities_balance = mongo.db.utilities_balance
            current_balance = utilities_balance.find_one({
                'user_email': self.test_user['email'],
                'utility_type': self.test_user['utility_type']
            })
            
            return current_balance

if __name__ == '__main__':
    # Run single test
    test = TestMeterRecharge()
    test.setup_class()
    test.test_valid_recharge()
def test_meter_recharge():
    test_data = {
        'user_email': 'leonard1@gmail.com',  # Use an email you know exists in the database
        'utility_type': 'water',     # Match the utility type in your database
        'token': '8604-9933-2693-8672',   # Use a valid token 13 units of water
        'units': 13,
        'timestamp': datetime.now().isoformat()
    }
    
    response = requests.post(
        'http://localhost:5000/api/utilities/process-meter-recharge',
        json=test_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")