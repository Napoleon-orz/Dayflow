from src.extensions import db


class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    date_of_joining = db.Column(db.Date)
    profile_picture_url = db.Column(db.String(255))

    user = db.relationship("User", backref=db.backref("profile", uselist=False))

    def __repr__(self):
        return f"<EmployeeProfile user_id={self.user_id}>"
