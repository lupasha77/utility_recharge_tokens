# services/stripe.py
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

stripe.api_key = "your_stripe_secret_key"

@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        data = request.json
        amount = data["amount"]
        currency = "usd"

        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            payment_method_types=["card"],
        )

        return jsonify({"clientSecret": payment_intent.client_secret})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
