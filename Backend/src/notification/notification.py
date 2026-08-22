"""
src/notification/notification.py
"""

from datetime import datetime
from src.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), default="info")  # info, warning, alert
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("notifications", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "isRead": self.is_read,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
