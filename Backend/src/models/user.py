from datetime import datetime
from src.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "admin" or "employee"
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------- Password helpers ----------
    def set_password(self, raw_password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    # ---------- Role determination from email ----------
    @staticmethod
    def determine_role(email: str) -> str | None:
        """
        Rule:
        - email containing 'odooadmin'  -> admin
        - email containing 'odoo' (but not 'odooadmin') -> employee
        - anything else -> None (signup should be rejected)

        NOTE: check 'odooadmin' before 'odoo' since 'odooadmin'
        also contains the substring 'odoo'.
        """
        email = email.lower().strip()
        if "odooadmin" in email:
            return "admin"
        elif "odoo" in email:
            return "employee"
        return None

    def __repr__(self):
        return f"<User {self.employee_id} ({self.role})>"
