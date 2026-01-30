# backend/app/trainer_routes.py
from flask import Blueprint, request, jsonify
from . import db
from .models import Trainer

trainer_bp = Blueprint("trainer_bp", __name__)

@trainer_bp.route("/trainers", methods=["GET"])
def get_trainers():
    q = request.args.get("q","").strip()
    if q:
        items = Trainer.query.filter((Trainer.name.ilike(f"%{q}%")) | (Trainer.specialization.ilike(f"%{q}%"))).all()
    else:
        items = Trainer.query.all()
    return jsonify([{"id":t.id,"name":t.name,"specialization":t.specialization,"salary":t.salary} for t in items])

@trainer_bp.route("/trainers/<int:tid>", methods=["GET"])
def get_trainer(tid):
    t = Trainer.query.get_or_404(tid)
    return jsonify({"id":t.id,"name":t.name,"specialization":t.specialization,"salary":t.salary})

@trainer_bp.route("/trainers", methods=["POST"])
def add_trainer():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("specialization"):
        return jsonify({"error":"name and specialization required"}), 400
    tr = Trainer(name=data["name"], specialization=data["specialization"], salary=float(data.get("salary",0)))
    db.session.add(tr); db.session.commit()
    return jsonify({"message":"trainer added","id":tr.id}), 201

@trainer_bp.route("/trainers/<int:tid>", methods=["PUT"])
def update_trainer(tid):
    t = Trainer.query.get_or_404(tid)
    data = request.get_json() or {}
    t.name = data.get("name", t.name); t.specialization = data.get("specialization", t.specialization)
    if "salary" in data: t.salary = float(data.get("salary", t.salary))
    db.session.commit(); return jsonify({"message":"trainer updated"})

@trainer_bp.route("/trainers/<int:tid>", methods=["DELETE"])
def delete_trainer(tid):
    t = Trainer.query.get_or_404(tid)
    db.session.delete(t); db.session.commit(); return jsonify({"message":"trainer deleted"})
