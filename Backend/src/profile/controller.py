from flask import jsonify, request, session
from src.extensions import db
from src.models.user import User
from src.profile.profile import Profile
from src.auth.decorators import login_required


def _get_or_create_profile(user_id):
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile


@login_required
def get_my_profile():
    user = User.query.get(session["user_id"])
    profile = _get_or_create_profile(user.id)

    data = profile.to_dict()
    data.update({
        "name": user.name,
        "email": user.email,
        "employeeId": user.employee_id,
        "role": user.role,
    })
    return jsonify({"profile": data}), 200


@login_required
def update_my_profile():
    data = request.get_json() or {}
    profile = _get_or_create_profile(session["user_id"])

    # Employees may only edit phone & address from this endpoint (matches the
    # "Edit Contact Details" form). Salary/job fields are admin-only and are
    # updated via /api/admin/salaries instead.
    if "phone" in data:
        profile.phone = data["phone"]
    if "address" in data:
        profile.address = data["address"]

    db.session.commit()
    return jsonify({"profile": profile.to_dict()}), 200
