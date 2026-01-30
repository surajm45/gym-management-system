# backend/app/payment_routes.py
from flask import Blueprint, request, jsonify
from . import db
from .models import Payment, Member, Plan
from datetime import datetime

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/payments", methods=["GET"])
def list_payments():
    q = request.args.get("q","").strip()
    rows = Payment.query.order_by(Payment.date.desc())
    if q:
        rows = rows.filter((Payment.method.ilike(f"%{q}%")) | (Payment.amount.cast(db.String).ilike(f"%{q}%")))
    rows = rows.all()
    out=[]
    for p in rows:
        member = Member.query.get(p.member_id)
        plan_name = None
        if member and member.plan_id:
            plan = Plan.query.get(member.plan_id); plan_name = plan.name if plan else None
        out.append({
            "id":p.id,"member_id":p.member_id,"member_name": member.name if member else None,
            "plan_name": plan_name,"amount":p.amount,"method":p.method,"date":p.date.isoformat() if p.date else None
        })
    return jsonify(out)

@payment_bp.route("/payments/<int:pid>", methods=["GET"])
def get_payment(pid):
    p = Payment.query.get_or_404(pid)
    return jsonify({"id":p.id,"member_id":p.member_id,"amount":p.amount,"method":p.method,"date":p.date.isoformat()})

@payment_bp.route("/payments", methods=["POST"])
def add_payment():
    data = request.get_json() or {}
    member_id = data.get("member_id"); amount = data.get("amount")
    if not member_id or amount is None:
        return jsonify({"error":"member_id and amount required"}), 400
    member = Member.query.get(member_id)
    if not member: return jsonify({"error":"member not found"}), 404
    p = Payment(member_id=member_id, amount=float(amount), method=data.get("method"), date=datetime.utcnow())
    db.session.add(p); db.session.commit(); return jsonify({"message":"payment added","id":p.id}), 201

@payment_bp.route("/payments/<int:pid>", methods=["PUT"])
def update_payment(pid):
    p = Payment.query.get_or_404(pid)
    data = request.get_json() or {}
    if "member_id" in data:
        m = Member.query.get(data.get("member_id")); 
        if not m: return jsonify({"error":"member not found"}), 404
        p.member_id = data.get("member_id")
    if "amount" in data: p.amount = float(data.get("amount"))
    if "method" in data: p.method = data.get("method")
    db.session.commit(); return jsonify({"message":"payment updated"})

@payment_bp.route("/payments/<int:pid>", methods=["DELETE"])
def delete_payment(pid):
    p = Payment.query.get_or_404(pid)
    db.session.delete(p); db.session.commit(); return jsonify({"message":"payment deleted"})
