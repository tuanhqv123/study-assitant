from flask import Flask
from flask_cors import CORS
from .routes.chat import chat_bp
from .routes.auth import auth_bp
from .routes.file_routes import file_bp
from .utils.logger import Logger

logger = Logger()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})  # Enable CORS for all routes

    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp, url_prefix='/file')

    return app