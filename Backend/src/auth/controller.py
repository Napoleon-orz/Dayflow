from flask import request, jsonify, session
from src.extensions import db
from src.models.user import User


# ============================================================
# SIGNUP
# ============================================================
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided."}), 400

    email = data.get("email", "").strip().lower()
    name = data.get("name")
    password = data.get("password")
    employee_id = data.get("employee_id")
    requested_role = data.get("role")  # "admin" or "employee", chosen in the signup form

    # 1. Basic field validation
    if not all([email, name, password, employee_id, requested_role]):
        return jsonify({"error": "All fields (name, email, password, employee_id, role) are required."}), 400

    # 2. Determine what role this email is actually allowed to have
    allowed_role = User.determine_role(email)

    if allowed_role is None:
        return jsonify({
            "error": "Signup denied. Email must contain 'odoo' (employee) or 'odooadmin' (admin)."
        }), 400

    # 3. Enforce that requested role matches what the email allows
    if requested_role != allowed_role:
        return jsonify({
            "error": f"This email is only eligible to sign up as '{allowed_role}', not '{requested_role}'."
        }), 403

    # 4. Check for duplicates
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 409
    if User.query.filter_by(employee_id=employee_id).first():
        return jsonify({"error": "Employee ID already exists."}), 409

    # 5. Create and save the user
    user = User(
        employee_id=employee_id,
        name=name,
        email=email,
        role=allowed_role,
        is_verified=False,  # flip to True once email verification is implemented
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Signup successful.",
        "user": {
            "id": user.id,
            "employee_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    }), 201


# ============================================================
# LOGIN
# ============================================================
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided."}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()

    # Generic error message on purpose — don't reveal whether email or password was wrong
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    # Store identifying info in the session (cookie-based)
    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "employee_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    }), 200


# ============================================================
# LOGOUT
# ============================================================
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


# ============================================================
# GET CURRENT LOGGED-IN USER (used by frontend to check session on page load)
# ============================================================
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Not logged in."}), 401

    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({"error": "User not found."}), 404

    return jsonify({
        "user": {
            "id": user.id,
            "employee_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    }), 200