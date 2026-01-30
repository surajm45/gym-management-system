# backend/app/equipment_routes.py
from flask import Blueprint, request, jsonify
from . import db
from .models import Equipment

equipment_bp = Blueprint("equipment_bp", __name__)

@equipment_bp.route("/equipment", methods=["GET"])
def list_equipment():
    q = request.args.get("q","").strip()
    if q:
        items = Equipment.query.filter((Equipment.name.ilike(f"%{q}%")) | (Equipment.category.ilike(f"%{q}%"))).all()
    else:
        items = Equipment.query.all()
    return jsonify([{"id":e.id,"name":e.name,"category":e.category,"quantity":e.quantity,"condition":e.condition} for e in items])

@equipment_bp.route("/equipment/<int:eid>", methods=["GET"])
def get_equipment(eid):
    e = Equipment.query.get_or_404(eid)
    return jsonify({"id":e.id,"name":e.name,"category":e.category,"quantity":e.quantity,"condition":e.condition})

@equipment_bp.route("/equipment", methods=["POST"])
def add_equipment():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("category"):
        return jsonify({"error":"name and category required"}), 400
    eq = Equipment(name=data["name"], category=data["category"], quantity=int(data.get("quantity",0)), condition=data.get("condition","Good"))
    db.session.add(eq); db.session.commit(); return jsonify({"message":"equipment added","id":eq.id}),201

@equipment_bp.route("/equipment/<int:eid>", methods=["PUT"])
def update_equipment(eid):
    e = Equipment.query.get_or_404(eid)
    data = request.get_json() or {}
    e.name = data.get("name", e.name); e.category = data.get("category", e.category)
    if "quantity" in data: e.quantity = int(data.get("quantity", e.quantity))
    if "condition" in data: e.condition = data.get("condition", e.condition)
    db.session.commit(); return jsonify({"message":"equipment updated"})

@equipment_bp.route("/equipment/<int:eid>", methods=["DELETE"])
def delete_equipment(eid):
    e = Equipment.query.get_or_404(eid)
    db.session.delete(e); db.session.commit(); return jsonify({"message":"equipment deleted"})
