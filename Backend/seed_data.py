"""
Run this once to populate the database with 10 sample users:
- 2 Admins   (email contains 'odooadmin')
- 8 Employees (email contains 'odoo' but not 'odooadmin')

Usage:
    python seed_data.py
"""

from src import create_app
from src.extensions import db
from src.models.user import User

app = create_app()

# (name, employee_id, email)  -- role is auto-derived from email
SAMPLE_USERS = [
    # ---- Admins (2) ----
    ("Aditi Sharma",   "EMP001", "aditi.sharma@odooadmin.com"),
    ("Rahul Verma",    "EMP002", "rahul.verma@odooadmin.com"),

    # ---- Employees (8) ----
    ("Priya Nair",     "EMP003", "priya.nair@odoo.com"),
    ("Karan Mehta",    "EMP004", "karan.mehta@odoo.com"),
    ("Sneha Reddy",    "EMP005", "sneha.reddy@odoo.com"),
    ("Arjun Iyer",     "EMP006", "arjun.iyer@odoo.com"),
    ("Neha Kapoor",    "EMP007", "neha.kapoor@odoo.com"),
    ("Vikram Singh",   "EMP008", "vikram.singh@odoo.com"),
    ("Ishita Das",     "EMP009", "ishita.das@odoo.com"),
    ("Rohan Gupta",    "EMP010", "rohan.gupta@odoo.com"),
]

DEFAULT_PASSWORD = "Password@123"  # change / hash per-user if you want variety


def seed():
    with app.app_context():
        db.create_all()

        created, skipped = 0, 0

        for name, emp_id, email in SAMPLE_USERS:
            if User.query.filter_by(email=email).first():
                skipped += 1
                continue

            role = User.determine_role(email)  # "admin" or "employee"
            if role is None:
                print(f"Skipping {email} — doesn't match odoo/odooadmin rule")
                continue

            user = User(
                employee_id=emp_id,
                name=name,
                email=email,
                role=role,
                is_verified=True,
            )
            user.set_password(DEFAULT_PASSWORD)

            db.session.add(user)
            created += 1

        db.session.commit()
        print(f"Seed complete. Created: {created}, Skipped (already existed): {skipped}")

        # quick summary
        admins = User.query.filter_by(role="admin").count()
        employees = User.query.filter_by(role="employee").count()
        print(f"Total in DB -> Admins: {admins}, Employees: {employees}")


if __name__ == "__main__":
    seed()