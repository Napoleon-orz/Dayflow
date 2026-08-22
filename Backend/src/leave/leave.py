import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
client = MongoClient(os.getenv("MONGO_URI"))
db = client["dayflow"]
users_collection = db["users"]
profiles_collection = db["profiles"]
leaves_collection = db["leaves"]

JWT_SECRET = os.getenv("JWT_SECRET")

# ---------- HELPERS ----------
def create_token(user_id, role):
    payload = {
        "id": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def serialize_profile(profile):
    profile["_id"] = str(profile["_id"])
    profile["userId"] = str(profile["userId"])
    return profile

def serialize_leave(leave):
    leave["_id"] = str(leave["_id"])
    leave["userId"] = str(leave["userId"])
    return leave

# ---------- AUTH MIDDLEWARE (decorators) ----------
def protect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "error": "No token provided"}), 401
        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = decoded  # contains id and role
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user.get("role") != "admin":
            return jsonify({"success": False, "error": "Admin access only"}), 403
        return f(*args, **kwargs)
    return decorated

# ---------- HEALTH CHECK ----------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ---------- AUTH ROUTES ----------
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    employee_id = data.get("employeeId")
    role = data.get("role", "employee")

    if users_collection.find_one({"email": email}):
        return jsonify({"success": False, "error": "Email already registered"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    user = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "employeeId": employee_id,
        "role": role
    }
    result = users_collection.insert_one(user)
    token = create_token(result.inserted_id, role)

    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": {"id": str(result.inserted_id), "name": name, "email": email, "role": role}
        }
    }), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"success": False, "error": "Invalid credentials"}), 400

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"success": False, "error": "Invalid credentials"}), 400

    token = create_token(user["_id"], user["role"])

    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user["role"]}
        }
    })

# ---------- PROFILE ROUTES ----------

# GET own profile
@app.route("/api/profile/me", methods=["GET"])
@protect
def get_my_profile():
    user_id = request.user["id"]
    profile = profiles_collection.find_one({"userId": ObjectId(user_id)})

    if not profile:
        # create an empty profile if one doesn't exist yet
        default_profile = {
            "userId": ObjectId(user_id),
            "phone": "",
            "address": "",
            "dateOfBirth": "",
            "gender": "",
            "jobTitle": "",
            "department": "",
            "dateOfJoining": "",
            "employmentType": "Full-time",
            "basicSalary": 0,
            "allowances": 0,
            "deductions": 0,
            "documents": [],
            "profilePictureUrl": ""
        }
        result = profiles_collection.insert_one(default_profile)
        profile = profiles_collection.find_one({"_id": result.inserted_id})

    return jsonify({"success": True, "data": serialize_profile(profile)})

# UPDATE own profile (limited fields — phone, address, profile picture)
@app.route("/api/profile/me", methods=["PUT"])
@protect
def update_my_profile():
    user_id = request.user["id"]
    data = request.get_json()

    allowed_updates = {
        "phone": data.get("phone"),
        "address": data.get("address"),
        "profilePictureUrl": data.get("profilePictureUrl")
    }
    # remove any fields that weren't sent
    allowed_updates = {k: v for k, v in allowed_updates.items() if v is not None}

    profiles_collection.update_one(
        {"userId": ObjectId(user_id)},
        {"$set": allowed_updates},
        upsert=True
    )
    profile = profiles_collection.find_one({"userId": ObjectId(user_id)})
    return jsonify({"success": True, "data": serialize_profile(profile)})

# ADMIN: get any employee's profile
@app.route("/api/profile/<user_id>", methods=["GET"])
@protect
@require_admin
def get_employee_profile(user_id):
    profile = profiles_collection.find_one({"userId": ObjectId(user_id)})
    if not profile:
        return jsonify({"success": False, "error": "Profile not found"}), 404
    return jsonify({"success": True, "data": serialize_profile(profile)})

# ADMIN: update any employee's full profile (job details, salary, etc.)
@app.route("/api/profile/<user_id>", methods=["PUT"])
@protect
@require_admin
def update_employee_profile(user_id):
    data = request.get_json()

    profiles_collection.update_one(
        {"userId": ObjectId(user_id)},
        {"$set": data},
        upsert=True
    )
    profile = profiles_collection.find_one({"userId": ObjectId(user_id)})
    return jsonify({"success": True, "data": serialize_profile(profile)})

# ---------- LEAVE ROUTES ----------

VALID_LEAVE_TYPES = ["paid", "sick", "unpaid"]
VALID_STATUSES = ["pending", "approved", "rejected"]

# APPLY FOR LEAVE (Employee)
@app.route("/api/leave/apply", methods=["POST"])
@protect
def apply_leave():
    data = request.get_json()
    leave_type = data.get("leaveType")
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    remarks = data.get("remarks", "")

    if leave_type not in VALID_LEAVE_TYPES:
        return jsonify({"success": False, "error": f"leaveType must be one of {VALID_LEAVE_TYPES}"}), 400

    if not start_date or not end_date:
        return jsonify({"success": False, "error": "startDate and endDate are required"}), 400

    leave = {
        "userId": ObjectId(request.user["id"]),
        "leaveType": leave_type,
        "startDate": start_date,
        "endDate": end_date,
        "remarks": remarks,
        "status": "pending",
        "adminComment": "",
        "reviewedBy": None,
        "createdAt": datetime.utcnow()
    }

    result = leaves_collection.insert_one(leave)
    leave["_id"] = result.inserted_id

    return jsonify({"success": True, "data": serialize_leave(leave)}), 201

# GET own leave requests (Employee)
@app.route("/api/leave/me", methods=["GET"])
@protect
def get_my_leaves():
    user_id = request.user["id"]
    leaves = list(leaves_collection.find({"userId": ObjectId(user_id)}).sort("createdAt", -1))
    leaves = [serialize_leave(l) for l in leaves]
    return jsonify({"success": True, "data": leaves})

# GET a single leave request by ID
@app.route("/api/leave/<leave_id>", methods=["GET"])
@protect
def get_leave_by_id(leave_id):
    leave = leaves_collection.find_one({"_id": ObjectId(leave_id)})
    if not leave:
        return jsonify({"success": False, "error": "Leave request not found"}), 404

    if request.user["role"] != "admin" and str(leave["userId"]) != request.user["id"]:
        return jsonify({"success": False, "error": "Not authorized to view this leave request"}), 403

    return jsonify({"success": True, "data": serialize_leave(leave)})

# GET all leave requests (Admin)
@app.route("/api/leave/all", methods=["GET"])
@protect
@require_admin
def get_all_leaves():
    status_filter = request.args.get("status")
    query = {}
    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"success": False, "error": f"status must be one of {VALID_STATUSES}"}), 400
        query["status"] = status_filter

    leaves = list(leaves_collection.find(query).sort("createdAt", -1))
    leaves = [serialize_leave(l) for l in leaves]
    return jsonify({"success": True, "data": leaves})

# APPROVE or REJECT a leave request (Admin)
@app.route("/api/leave/<leave_id>/review", methods=["PUT"])
@protect
@require_admin
def review_leave(leave_id):
    data = request.get_json()
    new_status = data.get("status")
    admin_comment = data.get("adminComment", "")

    if new_status not in ["approved", "rejected"]:
        return jsonify({"success": False, "error": "status must be 'approved' or 'rejected'"}), 400

    leave = leaves_collection.find_one({"_id": ObjectId(leave_id)})
    if not leave:
        return jsonify({"success": False, "error": "Leave request not found"}), 404

    if leave["status"] != "pending":
        return jsonify({
            "success": False,
            "error": f"Cannot change status — this request is already '{leave['status']}'"
        }), 400

    leaves_collection.update_one(
        {"_id": ObjectId(leave_id)},
        {"$set": {
            "status": new_status,
            "adminComment": admin_comment,
            "reviewedBy": request.user["id"]
        }}
    )

    updated_leave = leaves_collection.find_one({"_id": ObjectId(leave_id)})
    return jsonify({"success": True, "data": serialize_leave(updated_leave)})

# ---------- RUN SERVER ----------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
    