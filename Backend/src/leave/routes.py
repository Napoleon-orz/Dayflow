from flask import Blueprint
from src.leave.controller import apply_leave, my_leaves

leave_bp = Blueprint("leave", __name__, url_prefix="/api/leave")

leave_bp.route("", methods=["POST"])(apply_leave)
leave_bp.route("/me", methods=["GET"])(my_leaves)
