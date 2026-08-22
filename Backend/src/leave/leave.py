"""
src/leave/leave.py
"""

from datetime import datetime
from src.extensions import db


class Leave(db.Model):
    __tablename__ = "leaves"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    leave_type = db.Column(db.String(30), nullable=False)  # sick, casual, paid, unpaid
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255), default="")

    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", foreign_keys=[user_id], backref=db.backref("leave_requests", lazy=True))
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "leaveType": self.leave_type,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "reason": self.reason,
            "status": self.status,
            "reviewedBy": self.reviewed_by,
            "appliedAt": self.applied_at.isoformat() if self.applied_at else None,
            "reviewedAt": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
