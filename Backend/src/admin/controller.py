from datetime import date, datetime
from flask import jsonify, request, session
from src.extensions import db
from src.models.user import User
from src.profile.profile import Profile
from src.attendance.attendance import Attendance
from src.leave.leave import Leave
from src.auth.decorators import admin_required


def _profile_for(user):
    profile = Profile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
    return profile


@admin_required
def list_employees():
    today = date.today()
    users = User.query.order_by(User.name).all()

    result = []
    for u in users:
        profile = Profile.query.filter_by(user_id=u.id).first()
        record = Attendance.query.filter_by(user_id=u.id, date=today).first()
        result.append({
            "id": u.id,
            "employeeId": u.employee_id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "department": profile.department if profile else "",
            "todayStatus": record.status if record else "absent",
        })
    return jsonify({"employees": result}), 200


@admin_required
def employee_detail(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Employee not found."}), 404
    attendance = (
        Attendance.query.filter_by(user_id=user_id)
        .order_by(Attendance.date.desc())
        .limit(5)
        .all()
    )
    leaves = (
        Leave.query.filter_by(user_id=user_id)
        .order_by(Leave.applied_at.desc())
        .limit(5)
        .all()
    )
    return jsonify({
        "employee": {
            "id": user.id,
            "employeeId": user.employee_id,
            "name": user.name,
            "email": user.email,
        },
        "attendance": [a.to_dict() for a in attendance],
        "leaves": [l.to_dict() for l in leaves],
    }), 200


@admin_required
def list_all_leaves():
    pending = Leave.query.filter_by(status="pending").order_by(Leave.applied_at.desc()).all()
    resolved = Leave.query.filter(Leave.status != "pending").order_by(Leave.applied_at.desc()).all()

    def enrich(l):
        d = l.to_dict()
        d["employeeName"] = l.user.name if l.user else l.user_id
        d["employeeEmail"] = l.user.email if l.user else ""
        return d

    return jsonify({"leaves": [enrich(l) for l in pending + resolved]}), 200


@admin_required
def review_leave(leave_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ("approved", "rejected"):
        return jsonify({"error": "status must be 'approved' or 'rejected'."}), 400

    leave = Leave.query.get(leave_id)
    if not leave:
        return jsonify({"error": "Leave request not found."}), 404
    leave.status = new_status
    leave.reviewed_by = session["user_id"]
    leave.reviewed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"leave": leave.to_dict()}), 200


@admin_required
def list_salaries():
    users = User.query.order_by(User.name).all()
    result = []
    for u in users:
        profile = _profile_for(u)
        result.append({
            "userId": u.id,
            "name": u.name,
            "basicSalary": profile.basic_salary,
            "allowances": profile.allowances,
            "deductions": profile.deductions,
            "netSalary": profile.basic_salary + profile.allowances - profile.deductions,
        })
    return jsonify({"salaries": result}), 200


@admin_required
def update_salary(user_id):
    data = request.get_json() or {}
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Employee not found."}), 404
    profile = _profile_for(user)

    try:
        profile.basic_salary = float(data.get("basicSalary", profile.basic_salary))
        profile.allowances = float(data.get("allowances", profile.allowances))
        profile.deductions = float(data.get("deductions", profile.deductions))
    except (TypeError, ValueError):
        return jsonify({"error": "Salary fields must be numbers."}), 400

    db.session.commit()
    return jsonify({"salary": {
        "userId": user.id,
        "basicSalary": profile.basic_salary,
        "allowances": profile.allowances,
        "deductions": profile.deductions,
        "netSalary": profile.basic_salary + profile.allowances - profile.deductions,
    }}), 200
