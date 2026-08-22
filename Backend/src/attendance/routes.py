from flask import Blueprint
from src.attendance.controller import check_in, check_out, my_attendance

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")

attendance_bp.route("/checkin", methods=["POST"])(check_in)
attendance_bp.route("/checkout", methods=["POST"])(check_out)
attendance_bp.route("/me", methods=["GET"])(my_attendance)
