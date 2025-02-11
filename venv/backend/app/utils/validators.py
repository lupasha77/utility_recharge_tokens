 
# app/utils/validators.py
import re

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength.
    Returns (is_valid, message) tuple.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    checks = [
        (any(c.isupper() for c in password), "Password must contain at least one uppercase letter"),
        (any(c.islower() for c in password), "Password must contain at least one lowercase letter"),
        (any(c.isdigit() for c in password), "Password must contain at least one number"),
        (any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password), 
         "Password must contain at least one special character")
    ]
    
    for check, message in checks:
        if not check:
            return False, message
            
    return True, "Password is strong"

# app/validators/utility_validator.py
def validate_calculation_input(data):
    """Validate calculation input data"""
    if not data:
        return 'No data provided'
        
    if 'units' in data and 'amount' in data:
        return 'Provide either units or amount, not both'
        
    if 'units' in data:
        try:
            units = float(data['units'])
            if units <= 0:
                return 'Units must be greater than 0'
        except ValueError:
            return 'Invalid units value'
    elif 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return 'Amount must be greater than 0'
        except ValueError:
            return 'Invalid amount value'
    else:
        return 'Must provide either units or amount'
    
    return None