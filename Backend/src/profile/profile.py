"""
src/models/profile.py

SQLAlchemy Profile model — replaces the old Mongo `profiles_collection`.
Place this file next to your existing user.py model.
"""

from src.extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    phone = db.Column(db.String(20), default="")
    address = db.Column(db.String(255), default="")
    date_of_birth = db.Column(db.String(20), default="")   # switch to db.Date if you store real dates
    gender = db.Column(db.String(20), default="")

    job_title = db.Column(db.String(100), default="")
    department = db.Column(db.String(100), default="")
    date_of_joining = db.Column(db.String(20), default="")
    employment_type = db.Column(db.String(50), default="Full-time")

    basic_salary = db.Column(db.Float, default=0)
    allowances = db.Column(db.Float, default=0)
    deductions = db.Column(db.Float, default=0)

    documents = db.Column(db.JSON, default=list)           # requires MySQL 5.7.8+ for JSON columns
    profile_picture_url = db.Column(db.String(255), default="")

    user = db.relationship("User", backref=db.backref("hr_profile", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "phone": self.phone,
            "address": self.address,
            "dateOfBirth": self.date_of_birth,
            "gender": self.gender,
            "jobTitle": self.job_title,
            "department": self.department,
            "dateOfJoining": self.date_of_joining,
            "employmentType": self.employment_type,
            "basicSalary": self.basic_salary,
            "allowances": self.allowances,
            "deductions": self.deductions,
            "documents": self.documents or [],
            "profilePictureUrl": self.profile_picture_url,
        }
