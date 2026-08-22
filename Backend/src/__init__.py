from flask import Flask
from flask_cors import CORS

from src.config import Config
from src.extensions import db, bcrypt


def create_app():
    app = Flask(__name__, static_folder="../../frontend", static_url_path=""))
    app.config.from_object(Config)

    # Initialize extensions with this app
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)

    # Import every model so SQLAlchemy knows about it before create_all() runs.
    # NOTE: src/models/employee.py (EmployeeProfile) is a leftover/duplicate of
    # src/profile/profile.py (Profile) — seed_data.py and the rest of the app
    # use Profile, so EmployeeProfile is intentionally left unregistered here.
    from src.models import user  # noqa: F401
    from src.profile import profile  # noqa: F401
    from src.attendance import attendance  # noqa: F401
    from src.leave import leave  # noqa: F401
    from src.payroll import payroll  # noqa: F401
    from src.notification import notification  # noqa: F401
    from src.reports import report  # noqa: F401

    with app.app_context():
        db.create_all()

    # Register blueprints
    from src.auth.routes import auth_bp
    from src.profile.routes import profile_bp
    from src.attendance.routes import attendance_bp
    from src.leave.routes import leave_bp
    from src.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(admin_bp)

    # Serve the frontend from the same origin as the API so session cookies
    # just work, with no cross-site cookie configuration needed.
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app
