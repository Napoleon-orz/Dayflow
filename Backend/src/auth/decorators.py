from functools import wraps
from flask import session, jsonify


def login_required(f):
    """Blocks the request unless a valid session exists."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Not logged in."}), 401
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Blocks the request unless the session belongs to an admin."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Not logged in."}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "Admin access required."}), 403
        return f(*args, **kwargs)
    return wrapper
