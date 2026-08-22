"""
src/payroll/payroll.py
"""

from datetime import datetime
from src.extensions import db


class Payroll(db.Model):
    __tablename__ = "payroll"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)

    basic_salary = db.Column(db.Float, default=0)
    allowances = db.Column(db.Float, default=0)
    deductions = db.Column(db.Float, default=0)
    net_salary = db.Column(db.Float, default=0)

    status = db.Column(db.String(20), default="pending")  # pending, paid
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("payroll_records", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("user_id", "month", "year", name="uq_payroll_user_month_year"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "month": self.month,
            "year": self.year,
            "basicSalary": self.basic_salary,
            "allowances": self.allowances,
            "deductions": self.deductions,
            "netSalary": self.net_salary,
            "status": self.status,
            "generatedAt": self.generated_at.isoformat() if self.generated_at else None,
            "paidAt": self.paid_at.isoformat() if self.paid_at else None,
        }
