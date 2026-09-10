from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.student import Student
from app.utils import get_student_or_404

students_bp = Blueprint("students", __name__, url_prefix="/api/students")



@students_bp.route("", methods=["GET"])
@jwt_required()
def list_students():
    teacher_id = get_jwt_identity()
    students = Student.query.filter_by(teacher_id=int(teacher_id)).order_by(Student.first_name).all()
    # 2 aggregate queries total for all students, not 2 per student
    student_ids = [s.id for s in students]
    stats = Student.bulk_stats(student_ids)
    return jsonify([s.to_dict_with_stats(stats.get(s.id, {})) for s in students]), 200


@students_bp.route("", methods=["POST"])
@jwt_required()
def create_student():
    teacher_id = get_jwt_identity()
    data = request.get_json() or {}

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    if not first_name or not last_name:
        return jsonify({"error": "first_name and last_name are required"}), 400

    student = Student(
        teacher_id=int(teacher_id),
        first_name=first_name,
        last_name=last_name,
        grade=data.get("grade", ""),
        parent_name=data.get("parent_name", ""),
        parent_email=data.get("parent_email", ""),
        notes=data.get("notes", ""),
        strengths=data.get("strengths", ""),
        weaknesses=data.get("weaknesses", ""),
        status="active",
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@students_bp.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student.to_dict(include_stats=True)), 200


@students_bp.route("/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json() or {}
    for field in ["first_name", "last_name", "grade", "parent_name",
                  "parent_email", "notes", "strengths", "weaknesses", "status"]:
        if field in data:
            setattr(student, field, data[field])

    db.session.commit()
    return jsonify(student.to_dict(include_stats=True)), 200


@students_bp.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"}), 200
