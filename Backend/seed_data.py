"""
Run this once to populate the database with sample data across every module.

Usage:
    python seed_data.py
"""

import random
from datetime import date, datetime, timedelta

from src import create_app
from src.extensions import db
from src.models.user import User
from src.profile.profile import Profile
from src.attendance.attendance import Attendance
from src.leave.leave import Leave
from src.payroll.payroll import Payroll
from src.notification.notification import Notification
from src.reports.report import Report

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

DEPARTMENTS = ["Engineering", "Sales", "HR", "Finance", "Support"]
JOB_TITLES = ["Software Engineer", "Sales Executive", "HR Associate", "Accountant", "Support Specialist"]
LEAVE_TYPES = ["sick", "casual", "paid", "unpaid"]
ATTENDANCE_STATUSES = ["present", "present", "present", "late", "absent"]  # weighted toward present

DEFAULT_PASSWORD = "Password@123"


def seed_users_and_profiles():
    users_by_email = {}

    for name, emp_id, email in SAMPLE_USERS:
        existing = User.query.filter_by(email=email).first()
        if existing:
            users_by_email[email] = existing
            continue

        role = User.determine_role(email)
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
        db.session.flush()  # get user.id before commit
        users_by_email[email] = user

    db.session.commit()

    # Profiles
    for i, (name, emp_id, email) in enumerate(SAMPLE_USERS):
        user = users_by_email.get(email)
        if not user:
            continue
        if Profile.query.filter_by(user_id=user.id).first():
            continue

        profile = Profile(
            user_id=user.id,
            phone=f"98765{43210 - i:05d}",
            address=f"{100 + i} MG Road, Bengaluru, KA",
            date_of_birth=f"199{i % 10}-0{(i % 9) + 1}-15",
            gender="unspecified",
            job_title="HR Manager" if user.role == "admin" else JOB_TITLES[i % len(JOB_TITLES)],
            department="HR" if user.role == "admin" else DEPARTMENTS[i % len(DEPARTMENTS)],
            date_of_joining=f"2023-0{(i % 9) + 1}-01",
            employment_type="Full-time",
            basic_salary=60000 + (i * 2500),
            allowances=5000,
            deductions=1200,
            profile_picture_url="",
        )
        db.session.add(profile)

    db.session.commit()
    return users_by_email


def seed_attendance(users_by_email):
    today = date.today()
    count = 0

    for email, user in users_by_email.items():
        for days_ago in range(14):  # last 14 days
            day = today - timedelta(days=days_ago)
            if day.weekday() >= 5:  # skip weekends
                continue
            if Attendance.query.filter_by(user_id=user.id, date=day).first():
                continue

            status = random.choice(ATTENDANCE_STATUSES)
            check_in = None
            check_out = None
            if status in ("present", "late"):
                hour = 9 if status == "present" else random.choice([10, 11])
                check_in = datetime.combine(day, datetime.min.time()) + timedelta(hours=hour, minutes=random.randint(0, 59))
                check_out = check_in + timedelta(hours=8, minutes=random.randint(0, 30))

            db.session.add(Attendance(
                user_id=user.id,
                date=day,
                check_in=check_in,
                check_out=check_out,
                status=status,
            ))
            count += 1

    db.session.commit()
    print(f"Seeded {count} attendance records.")


def seed_leaves(users_by_email):
    admins = [u for u in users_by_email.values() if u.role == "admin"]
    reviewer = admins[0] if admins else None
    count = 0

    for email, user in users_by_email.items():
        if user.role == "admin":
            continue  # admins reviewing, not applying, in this sample set

        start = date.today() + timedelta(days=random.randint(5, 30))
        end = start + timedelta(days=random.randint(0, 3))
        status = random.choice(["pending", "approved", "rejected"])

        leave = Leave(
            user_id=user.id,
            leave_type=random.choice(LEAVE_TYPES),
            start_date=start,
            end_date=end,
            reason="Personal reasons",
            status=status,
            reviewed_by=reviewer.id if reviewer and status != "pending" else None,
            reviewed_at=datetime.utcnow() if status != "pending" else None,
        )
        db.session.add(leave)
        count += 1

    db.session.commit()
    print(f"Seeded {count} leave requests.")


def seed_payroll(users_by_email):
    today = date.today()
    count = 0

    for email, user in users_by_email.items():
        profile = Profile.query.filter_by(user_id=user.id).first()
        basic = profile.basic_salary if profile else 60000
        allowances = profile.allowances if profile else 5000
        deductions = profile.deductions if profile else 1200

        for months_ago in range(3):  # last 3 months
            month_date = today.replace(day=1) - timedelta(days=months_ago * 30)
            month, year = month_date.month, month_date.year

            if Payroll.query.filter_by(user_id=user.id, month=month, year=year).first():
                continue

            db.session.add(Payroll(
                user_id=user.id,
                month=month,
                year=year,
                basic_salary=basic,
                allowances=allowances,
                deductions=deductions,
                net_salary=basic + allowances - deductions,
                status="paid" if months_ago > 0 else "pending",
                paid_at=datetime.utcnow() if months_ago > 0 else None,
            ))
            count += 1

    db.session.commit()
    print(f"Seeded {count} payroll records.")


def seed_notifications(users_by_email):
    messages = [
        ("info", "Welcome!", "Welcome to Dayflow — your HR portal."),
        ("info", "Payroll processed", "Your latest payslip is now available."),
        ("warning", "Attendance reminder", "Don't forget to check in today."),
    ]
    count = 0

    for email, user in users_by_email.items():
        for ntype, title, message in messages:
            db.session.add(Notification(
                user_id=user.id,
                title=title,
                message=message,
                type=ntype,
                is_read=random.choice([True, False]),
            ))
            count += 1

    db.session.commit()
    print(f"Seeded {count} notifications.")


def seed_reports(users_by_email):
    admins = [u for u in users_by_email.values() if u.role == "admin"]
    if not admins:
        return

    today = date.today()
    reports = [
        ("attendance", today.replace(day=1), today),
        ("payroll", today.replace(day=1), today),
    ]

    for report_type, start, end in reports:
        db.session.add(Report(
            generated_by=admins[0].id,
            report_type=report_type,
            period_start=start,
            period_end=end,
            file_url=f"/reports/{report_type}-{today.isoformat()}.pdf",
        ))

    db.session.commit()
    print(f"Seeded {len(reports)} report logs.")


def seed():
    with app.app_context():
        db.create_all()

        users_by_email = seed_users_and_profiles()
        print(f"Users + profiles ready: {len(users_by_email)} users.")

        seed_attendance(users_by_email)
        seed_leaves(users_by_email)
        seed_payroll(users_by_email)
        seed_notifications(users_by_email)
        seed_reports(users_by_email)

        admins = User.query.filter_by(role="admin").count()
        employees = User.query.filter_by(role="employee").count()
        print(f"Total in DB -> Admins: {admins}, Employees: {employees}")


if __name__ == "__main__":
    seed()
