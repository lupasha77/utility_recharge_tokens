#  app/services/paynowzw.py
import requests

PAYNOW_INTEGRATION_ID = "your_paynow_integration_id"
PAYNOW_INTEGRATION_KEY = "your_paynow_integration_key"

@app.route("/mobile-payment", methods=["POST"])
def mobile_payment():
    data = request.json
    amount = data["amount"]
    mobile_number = data["mobile_number"]
    method = data["method"]  # 'ecocash', 'onemoney', 'telecash'

    payload = {
        "id": PAYNOW_INTEGRATION_ID,
        "reference": "Invoice001",
        "amount": amount,
        "method": method,
        "mobile": mobile_number,
        "resulturl": "https://yourdomain.com/payment-result",
        "returnurl": "https://yourdomain.com/payment-success",
    }

    response = requests.post("https://www.paynow.co.zw/interface/initiatetransaction", json=payload)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Payment failed"}), 400
