from flask import Blueprint
from src.auth.controller import signup, login, logout, get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

auth_bp.route("/signup", methods=["POST"])(signup)
auth_bp.route("/login", methods=["POST"])(login)
auth_bp.route("/logout", methods=["POST"])(logout)
auth_bp.route("/me", methods=["GET"])(get_current_user)
