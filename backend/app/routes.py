# backend/app/routes.py
from flask import Blueprint, request, jsonify
from . import db
from .models import Member, Plan
from sqlalchemy.exc import IntegrityError

members_bp = Blueprint("members_bp", __name__)

@members_bp.route("/members", methods=["GET"])
def get_members():
    q = request.args.get("q", "").strip()
    if q:
        members = Member.query.filter(
            (Member.name.ilike(f"%{q}%")) |
            (Member.email.ilike(f"%{q}%")) |
            (Member.phone.ilike(f"%{q}%"))
        ).all()
    else:
        members = Member.query.all()
    out = []
    for m in members:
        out.append({"id": m.id, "name": m.name, "email": m.email, "phone": m.phone, "plan_id": m.plan_id})
    return jsonify(out), 200

@members_bp.route("/members/<int:m_id>", methods=["GET"])
def get_member(m_id):
    m = Member.query.get_or_404(m_id)
    return jsonify({"id": m.id, "name": m.name, "email": m.email, "phone": m.phone, "plan_id": m.plan_id})

@members_bp.route("/members", methods=["POST"])
def create_member():
    data = request.get_json() or {}
    name = data.get("name"); email = data.get("email"); phone = data.get("phone"); plan_id = data.get("plan_id")
    if not name or not email or not phone:
        return jsonify({"error": "name, email and phone required"}), 400
    if plan_id:
        if not Plan.query.get(plan_id):
            return jsonify({"error": "plan not found"}), 404
    try:
        m = Member(name=name, email=email, phone=phone, plan_id=plan_id)
        db.session.add(m); db.session.commit()
        return jsonify({"message": "member added", "id": m.id}), 201
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"error":"IntegrityError","detail":str(ie.orig.args)}), 400
    except Exception as e:
        db.session.rollback(); return jsonify({"error":str(e)}), 500

@members_bp.route("/members/<int:m_id>", methods=["PUT"])
def update_member(m_id):
    data = request.get_json() or {}
    m = Member.query.get_or_404(m_id)
    m.name = data.get("name", m.name)
    m.email = data.get("email", m.email)
    m.phone = data.get("phone", m.phone)
    if "plan_id" in data:
        plan_id = data.get("plan_id")
        if plan_id:
            if not Plan.query.get(plan_id):
                return jsonify({"error":"plan not found"}), 404
            m.plan_id = plan_id
        else:
            m.plan_id = None
    try:
        db.session.commit()
        return jsonify({"message":"member updated"})
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"error":"IntegrityError","detail":str(ie.orig.args)}), 400
    except Exception as e:
        db.session.rollback(); return jsonify({"error":str(e)}), 500

@members_bp.route("/members/<int:m_id>", methods=["DELETE"])
def delete_member(m_id):
    m = Member.query.get_or_404(m_id)
    try:
        db.session.delete(m); db.session.commit()
        return jsonify({"message":"member deleted"})
    except Exception as e:
        db.session.rollback(); return jsonify({"error":str(e)}), 500
