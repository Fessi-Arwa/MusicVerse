from flask import Flask, redirect, url_for
from .routes import library_bp, playlists_bp
from musicverse.core.database import init_db


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024
    
    # Initialize the database
    init_db()
    
    # Register blueprints
    app.register_blueprint(library_bp)
    app.register_blueprint(playlists_bp)

    @app.route("/")
    def home():
        """Send the root URL to the music library."""
        return redirect(url_for("library.library"))
    
    return app
