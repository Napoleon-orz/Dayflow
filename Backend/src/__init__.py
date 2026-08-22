from flask import Flask
from flask_cors import CORS

from src.config import Config
from src.extensions import db, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with this app
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)

    # Import models so SQLAlchemy knows about them before create_all() runs
    from src.models import user, employee  # noqa: F401

    # Register blueprints
    from src.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
