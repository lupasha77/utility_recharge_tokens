import requests
from PyQt6.QtCore import QObject, pyqtSignal

class TokenValidator(QObject):
    validation_complete = pyqtSignal(bool, str, float)
    
    def __init__(self, api_base_url):
        super().__init__()
        self.api_base_url = api_base_url
        
    def validate_token(self, token, headers):
        try:
            response = requests.post(
                f"{self.api_base_url}/transactions/validate-token",
                headers=headers,
                json={"token": token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.validation_complete.emit(True, "Token valid", float(data.get('units', 0)))
            else:
                self.validation_complete.emit(False, "Invalid token", 0)
        except Exception as e:
            self.validation_complete.emit(False, f"Error: {str(e)}", 0)