"""
src/reports/report.py

A log of generated reports (e.g. monthly attendance summary, payroll summary).
If "reports" in your app is meant to be purely computed on-the-fly (no stored
rows), you may not need this table at all — let me know and it can be dropped.
"""

from datetime import datetime
from src.extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    generated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    report_type = db.Column(db.String(50), nullable=False)  # attendance, payroll, leave, etc.
    period_start = db.Column(db.Date, nullable=True)
    period_end = db.Column(db.Date, nullable=True)

    file_url = db.Column(db.String(255), default="")
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    generator = db.relationship("User", backref=db.backref("generated_reports", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "generatedBy": self.generated_by,
            "reportType": self.report_type,
            "periodStart": self.period_start.isoformat() if self.period_start else None,
            "periodEnd": self.period_end.isoformat() if self.period_end else None,
            "fileUrl": self.file_url,
            "generatedAt": self.generated_at.isoformat() if self.generated_at else None,
        }
