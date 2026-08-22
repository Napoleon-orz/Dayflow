from flask import Blueprint
from src.admin.controller import (
    list_employees,
    employee_detail,
    list_all_leaves,
    review_leave,
    list_salaries,
    update_salary,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

admin_bp.route("/employees", methods=["GET"])(list_employees)
admin_bp.route("/employees/<int:user_id>", methods=["GET"])(employee_detail)
admin_bp.route("/leaves", methods=["GET"])(list_all_leaves)
admin_bp.route("/leaves/<int:leave_id>", methods=["PUT"])(review_leave)
admin_bp.route("/salaries", methods=["GET"])(list_salaries)
admin_bp.route("/salaries/<int:user_id>", methods=["PUT"])(update_salary)
