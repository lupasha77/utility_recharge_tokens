#  app/utils/utility_token_generator.py

import string
import random

def generate_recharge_token():
    """Generate a 16-digit token grouped in 4s"""
    digits = ''.join(random.choices(string.digits, k=16))
    return '-'.join([digits[i:i+4] for i in range(0, 16, 4)])