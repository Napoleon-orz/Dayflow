from datetime import datetime
from flask import jsonify, request, session
from src.extensions import db
from src.leave.leave import Leave
from src.auth.decorators import login_required


@login_required
def apply_leave():
    data = request.get_json() or {}
    leave_type = data.get("leaveType")
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    reason = data.get("reason", "")

    if not all([leave_type, start_date, end_date]):
        return jsonify({"error": "leaveType, startDate and endDate are required."}), 400

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Dates must be in YYYY-MM-DD format."}), 400

    if end < start:
        return jsonify({"error": "End date cannot be before start date."}), 400

    leave = Leave(
        user_id=session["user_id"],
        leave_type=leave_type,
        start_date=start,
        end_date=end,
        reason=reason,
    )
    db.session.add(leave)
    db.session.commit()
    return jsonify({"leave": leave.to_dict()}), 201


@login_required
def my_leaves():
    leaves = (
        Leave.query.filter_by(user_id=session["user_id"])
        .order_by(Leave.applied_at.desc())
        .all()
    )
    return jsonify({"leaves": [l.to_dict() for l in leaves]}), 200
