# backend/app/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from . import db, mail
from .models import OTP, User, Member
from datetime import datetime, timedelta
import random
from flask_mail import Message

auth_bp = Blueprint("auth_bp", __name__)

ADMIN_EMAIL = "moolyas794@gmail.com"

def _generate_code(n=6):
    return "".join(str(random.randint(0,9)) for _ in range(n))


# ======================================================
# ADMIN OTP REQUEST
# ======================================================

@auth_bp.route("/auth/request_otp", methods=["POST"])
def request_otp():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error":"email required"}), 400

    # generate code and expiry (10 minutes)
    code = _generate_code(6)
    now = datetime.utcnow()
    expires = now + timedelta(minutes=10)

    otp = OTP(email=email, code=code, created_at=now, expires_at=expires)
    db.session.add(otp)

    try:
        # auto-create user row if admin OTP login used first time
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, password="", role="admin" if email == ADMIN_EMAIL else "member")
            db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error":"internal error"}), 500

    try:
        mail_user = current_app.config.get("MAIL_USERNAME")
        subject = "Your Gym App OTP"
        body = f"Your one-time login code is: {code}\nIt expires in 10 minutes."

        if mail_user:
            msg = Message(subject=subject, recipients=[email], body=body, sender=mail_user)
            mail.send(msg)
            return jsonify({"message":"OTP sent"}), 200
        else:
            # development mode
            return jsonify({"message":"OTP (dev mode)", "dev_code": code}), 200

    except Exception:
        return jsonify({"error":"failed to send OTP"}), 500


# ======================================================
# ADMIN OTP VERIFICATION
# ======================================================

@auth_bp.route("/auth/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()
    if not email or not code:
        return jsonify({"error":"email and code required"}), 400

    now = datetime.utcnow()
    otp = OTP.query.filter_by(email=email, code=code).order_by(OTP.created_at.desc()).first()
    if not otp:
        return jsonify({"error":"invalid or expired code"}), 400

    if otp.expires_at and otp.expires_at < now:
        return jsonify({"error":"code expired"}), 400

    try:
        otp.expires_at = now
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({"message":"verified", "role":"admin"}), 200


# ======================================================
# MEMBER SIGNUP — CREATE USER + MEMBER PROFILE
# ======================================================

@auth_bp.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    gender = (data.get("gender") or "").strip()
    age = (data.get("age") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # ---------------- VALIDATION ----------------
    if not name or not gender or not age or not phone or not email or not password:
        return jsonify({"error": "all fields required"}), 400

    if email == ADMIN_EMAIL.lower():
        return jsonify({"error": "You cannot sign up using admin email"}), 400

    # check existing users
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 400

    # ---------------- CREATE LOGIN USER ----------------
    user = User(name=name, email=email, password=password, role="member")
    db.session.add(user)
    db.session.commit()

    # ---------------- CREATE MEMBER PROFILE ----------------
    member = Member(
        name=name,
        email=email,
        phone=phone,
        gender=gender,
        age=int(age)
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({"message": "Account created successfully"}), 201


# ======================================================
# LOGIN — ADMIN OR MEMBER
# ======================================================

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "user not found"}), 404

    # validate password
    if user.password != password:
        return jsonify({"error": "invalid password"}), 401

    return jsonify({
        "message": "login ok",
        "role": user.role
    }), 200
