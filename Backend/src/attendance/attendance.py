"""
src/attendance/attendance.py
"""

from datetime import datetime
from src.extensions import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="present")  # present, absent, late, half-day
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("attendance_records", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("user_id", "date", name="uq_attendance_user_date"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "checkIn": self.check_in.isoformat() if self.check_in else None,
            "checkOut": self.check_out.isoformat() if self.check_out else None,
            "status": self.status,
        }
