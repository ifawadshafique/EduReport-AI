from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.attendance import Attendance
from app.utils import get_student_or_404
import datetime

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/students/<int:student_id>/attendance", methods=["GET"])
@jwt_required()
def list_attendance(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    records = (
        Attendance.query.filter_by(student_id=student_id)
        .order_by(Attendance.date.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in records]), 200


@attendance_bp.route("/api/students/<int:student_id>/attendance", methods=["POST"])
@jwt_required()
def add_attendance(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json() or {}
    date_str = data.get("date", "")
    status = data.get("status", "present")

    if not date_str:
        return jsonify({"error": "date is required (YYYY-MM-DD)"}), 400
    if status not in ("present", "absent", "late", "excused"):
        return jsonify({"error": "status must be present / absent / late / excused"}), 400

    try:
        date = datetime.date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    record = Attendance(student_id=student_id, date=date, status=status)
    db.session.add(record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Attendance for {date_str} already exists. Edit the existing record instead."}), 409

    return jsonify(record.to_dict()), 201


@attendance_bp.route("/api/students/<int:student_id>/attendance/<int:att_id>", methods=["PUT"])
@jwt_required()
def update_attendance(student_id, att_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    record = Attendance.query.filter_by(id=att_id, student_id=student_id).first()
    if not record:
        return jsonify({"error": "Attendance record not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status", record.status)
    if new_status not in ("present", "absent", "late", "excused"):
        return jsonify({"error": "status must be present / absent / late / excused"}), 400

    record.status = new_status
    db.session.commit()
    return jsonify(record.to_dict()), 200


@attendance_bp.route("/api/students/<int:student_id>/attendance/<int:att_id>", methods=["DELETE"])
@jwt_required()
def delete_attendance(student_id, att_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    record = Attendance.query.filter_by(id=att_id, student_id=student_id).first()
    if not record:
        return jsonify({"error": "Attendance record not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Attendance record deleted"}), 200
