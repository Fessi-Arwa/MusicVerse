from flask import Flask


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    return app