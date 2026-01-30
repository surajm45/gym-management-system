# backend/app/plan_routes.py
from flask import Blueprint, request, jsonify
from . import db
from .models import Plan
from sqlalchemy.exc import IntegrityError

plan_bp = Blueprint("plan_bp", __name__)

@plan_bp.route("/plans", methods=["GET"])
def get_plans():
    q = request.args.get("q", "").strip()
    if q:
        plans = Plan.query.filter(Plan.name.ilike(f"%{q}%")).all()
    else:
        plans = Plan.query.all()
    return jsonify([{"id":p.id,"name":p.name,"price":p.price,"duration_days":p.duration_days} for p in plans])

@plan_bp.route("/plans/<int:pid>", methods=["GET"])
def get_plan(pid):
    p = Plan.query.get_or_404(pid)
    return jsonify({"id":p.id,"name":p.name,"price":p.price,"duration_days":p.duration_days})

@plan_bp.route("/plans", methods=["POST"])
def add_plan():
    data = request.get_json() or {}
    if not data.get("name") or data.get("price") is None:
        return jsonify({"error":"name and price required"}), 400
    try:
        p = Plan(name=data["name"], price=float(data["price"]), duration_days=int(data.get("duration_days",30)))
        db.session.add(p); db.session.commit()
        return jsonify({"message":"Plan added","id":p.id}), 201
    except Exception as e:
        db.session.rollback(); return jsonify({"error":str(e)}), 500

@plan_bp.route("/plans/<int:pid>", methods=["PUT"])
def update_plan(pid):
    p = Plan.query.get_or_404(pid)
    data = request.get_json() or {}
    p.name = data.get("name", p.name)
    if "price" in data: p.price = float(data.get("price", p.price))
    if "duration_days" in data: p.duration_days = int(data.get("duration_days", p.duration_days))
    try:
        db.session.commit(); return jsonify({"message":"plan updated"})
    except Exception as e:
        db.session.rollback(); return jsonify({"error":str(e)}), 500

@plan_bp.route("/plans/<int:pid>", methods=["DELETE"])
def delete_plan(pid):
    p = Plan.query.get_or_404(pid)
    try:
        db.session.delete(p); db.session.commit(); return jsonify({"message":"plan deleted"})
    except Exception as e:
        db.session.rollback(); return jsonify({"error":str(e)}), 500
