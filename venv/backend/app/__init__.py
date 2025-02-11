# // app/__init__.py
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
import os
import logging
from flask_jwt_extended import JWTManager


from dotenv import load_dotenv
load_dotenv()

mongo = PyMongo()
jwt = JWTManager()
mail = Mail()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production with HTTPS

    jwt = JWTManager(app)

    # Set up upload folder
    upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    app.config['UPLOAD_FOLDER'] = upload_folder

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"Created uploads folder at {upload_folder}")

  

    # Configure CORS
    # CORS(app, supports_credentials=True)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS","PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "send_wildcard": False,
            "max_age": 120
        }
    })

    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.verification import verification_bp
    from app.routes.token_jwt import token_jwt_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.messages import messages_bp
    from app.routes.utilities import utilities_bp
    from app.routes.wallet import wallet_bp
    from app.routes.uploads import upload_bp 
    from app.routes.wallets_transactions import wallets_transactions_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    app.register_blueprint(token_jwt_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(utilities_bp, url_prefix='/api/utilities')
    app.register_blueprint(upload_bp, url_prefix='/api/files')
    app.register_blueprint(wallets_transactions_bp, url_prefix='/api/wallets_transactions')

    return app


