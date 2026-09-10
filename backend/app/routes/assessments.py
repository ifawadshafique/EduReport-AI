from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.assessment import Assessment
from app.utils import get_student_or_404
import datetime

assessments_bp = Blueprint("assessments", __name__)


@assessments_bp.route("/api/students/<int:student_id>/assessments", methods=["GET"])
@jwt_required()
def list_assessments(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    records = (
        Assessment.query.filter_by(student_id=student_id)
        .order_by(Assessment.date.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in records]), 200


@assessments_bp.route("/api/students/<int:student_id>/assessments", methods=["POST"])
@jwt_required()
def add_assessment(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    try:
        max_marks = float(data.get("max_marks", 100))
        obtained_marks = float(data.get("obtained_marks", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "max_marks and obtained_marks must be numbers"}), 400

    if max_marks <= 0:
        return jsonify({"error": "max_marks must be greater than 0"}), 400

    # Core validation: score cannot exceed maximum
    if obtained_marks > max_marks:
        return jsonify({
            "error": f"obtained_marks ({obtained_marks}) cannot exceed max_marks ({max_marks})"
        }), 400

    if obtained_marks < 0:
        return jsonify({"error": "obtained_marks cannot be negative"}), 400

    assessment_type = data.get("type", "quiz")
    valid_types = ("quiz", "test", "assignment", "project", "exam", "homework")
    if assessment_type not in valid_types:
        return jsonify({"error": f"type must be one of: {', '.join(valid_types)}"}), 400

    date = None
    if data.get("date"):
        try:
            date = datetime.date.fromisoformat(data["date"])
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    assessment = Assessment(
        student_id=student_id,
        subject_id=data.get("subject_id") or None,
        name=name,
        type=assessment_type,
        max_marks=max_marks,
        obtained_marks=obtained_marks,
        date=date,
        comment=data.get("comment", ""),
    )
    db.session.add(assessment)
    db.session.commit()
    return jsonify(assessment.to_dict()), 201


@assessments_bp.route("/api/students/<int:student_id>/assessments/<int:assessment_id>", methods=["DELETE"])
@jwt_required()
def delete_assessment(student_id, assessment_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    assessment = Assessment.query.filter_by(id=assessment_id, student_id=student_id).first()
    if not assessment:
        return jsonify({"error": "Assessment not found"}), 404

    db.session.delete(assessment)
    db.session.commit()
    return jsonify({"message": "Assessment deleted"}), 200
