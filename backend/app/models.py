from . import db
from datetime import datetime

# -------------------- AUTH / USERS --------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    # optional full name for display
    name = db.Column(db.String(120), nullable=True)

    # unique login identity
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # password stored as string (you can later change to hashed)
    password = db.Column(db.String(200), nullable=False)

    # role: "admin" or "member" (default)
    role = db.Column(db.String(20), default="member", nullable=False)


# -------------------- CORE GYM TABLES --------------------

class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=True)

    payments = db.relationship("Payment", backref="member", lazy=True)
    attendance = db.relationship("Attendance", backref="member", lazy=True)
    gender = db.Column(db.String(20))
age = db.Column(db.Integer)



class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Equipment(db.Model):
    __tablename__ = "equipment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    purchased_date = db.Column(db.Date)


class Trainer(db.Model):
    __tablename__ = "trainers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.Float, nullable=False)


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), default="Present")


# -------------------- OTP FOR ADMIN LOGIN --------------------

class OTP(db.Model):
    __tablename__ = "otp"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    def is_valid(self):
        return self.expires_at is None or datetime.utcnow() < self.expires_at
