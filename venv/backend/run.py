# backend/run.py
from app import create_app

app = create_app()
from flask import Flask, jsonify

@app.route('/protected', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'message': 'Preflight OK'})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

if __name__ == '__main__':
    app.run(debug=True)
