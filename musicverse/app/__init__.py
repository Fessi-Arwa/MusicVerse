from flask import Flask
from .routes import library_bp, playlists_bp
from musicverse.core.database import init_db


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    
    # Initialize the database
    init_db()
    
    # Register blueprints
    app.register_blueprint(library_bp)
    app.register_blueprint(playlists_bp)
    
    return app