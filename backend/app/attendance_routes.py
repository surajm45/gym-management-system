# backend/app/attendance_routes.py
from flask import Blueprint, request, jsonify
from . import db
from .models import Attendance, Member
from datetime import datetime

attendance_bp = Blueprint("attendance_bp", __name__)

@attendance_bp.route("/attendance", methods=["GET"])
def list_attendance():
    q = request.args.get("q","").strip()
    rows = Attendance.query.order_by(Attendance.date.desc())
    if q:
        rows = rows.filter(Attendance.status.ilike(f"%{q}%"))
    rows = rows.all()
    out=[]
    for a in rows:
        out.append({"id":a.id,"member_id":a.member_id,"member_name": a.member.name if a.member else None, "status":a.status, "date":a.date.isoformat() if a.date else None})
    return jsonify(out)

@attendance_bp.route("/attendance/<int:aid>", methods=["GET"])
def get_attendance(aid):
    a = Attendance.query.get_or_404(aid)
    return jsonify({"id":a.id,"member_id":a.member_id,"status":a.status,"date":a.date.isoformat()})

@attendance_bp.route("/attendance", methods=["POST"])
def add_attendance():
    data = request.get_json() or {}
    member_id = data.get("member_id"); status = data.get("status","Present")
    if not member_id: return jsonify({"error":"member_id required"}), 400
    if not Member.query.get(member_id): return jsonify({"error":"member not found"}), 404
    a = Attendance(member_id=member_id, status=status, date=datetime.utcnow())
    db.session.add(a); db.session.commit(); return jsonify({"message":"attendance added","id":a.id}), 201

@attendance_bp.route("/attendance/<int:aid>", methods=["PUT"])
def update_attendance(aid):
    a = Attendance.query.get_or_404(aid); data = request.get_json() or {}
    if "member_id" in data:
        if not Member.query.get(data.get("member_id")): return jsonify({"error":"member not found"}), 404
        a.member_id = data.get("member_id")
    if "status" in data: a.status = data.get("status")
    db.session.commit(); return jsonify({"message":"attendance updated"})

@attendance_bp.route("/attendance/<int:aid>", methods=["DELETE"])
def delete_attendance(aid):
    a = Attendance.query.get_or_404(aid)
    db.session.delete(a); db.session.commit(); return jsonify({"message":"attendance deleted"})
