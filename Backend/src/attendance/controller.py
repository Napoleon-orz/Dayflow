from datetime import datetime, date
from flask import jsonify, session
from src.extensions import db
from src.attendance.attendance import Attendance
from src.auth.decorators import login_required


@login_required
def check_in():
    user_id = session["user_id"]
    today = date.today()

    existing = Attendance.query.filter_by(user_id=user_id, date=today).first()
    if existing:
        return jsonify({"error": "You've already checked in today."}), 409

    now = datetime.utcnow()
    status = "present" if now.hour < 10 else "late"

    record = Attendance(user_id=user_id, date=today, check_in=now, status=status)
    db.session.add(record)
    db.session.commit()
    return jsonify({"attendance": record.to_dict()}), 201


@login_required
def check_out():
    user_id = session["user_id"]
    today = date.today()

    existing = Attendance.query.filter_by(user_id=user_id, date=today).first()
    if not existing:
        return jsonify({"error": "You need to check in first."}), 400
    if existing.check_out:
        return jsonify({"error": "You've already checked out today."}), 409

    existing.check_out = datetime.utcnow()
    db.session.commit()
    return jsonify({"attendance": existing.to_dict()}), 200


@login_required
def my_attendance():
    user_id = session["user_id"]
    records = (
        Attendance.query.filter_by(user_id=user_id)
        .order_by(Attendance.date.desc())
        .all()
    )
    return jsonify({"attendance": [r.to_dict() for r in records]}), 200
