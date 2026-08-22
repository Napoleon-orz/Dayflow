from flask import Blueprint
from src.profile.controller import get_my_profile, update_my_profile

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")

profile_bp.route("/me", methods=["GET"])(get_my_profile)
profile_bp.route("/me", methods=["PUT"])(update_my_profile)
