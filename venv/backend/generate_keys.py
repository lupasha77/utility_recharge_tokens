# //backend/app/utils/generate_keys.py 
import os
import sys
from app.routes.messages import MessageEncryption

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))



if __name__ == "__main__":
    encryption = MessageEncryption()
    encryption.generate_new_keys()