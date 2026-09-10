from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.subject import Subject

subjects_bp = Blueprint("subjects", __name__, url_prefix="/api/subjects")


@subjects_bp.route("", methods=["GET"])
@jwt_required()
def list_subjects():
    teacher_id = get_jwt_identity()
    subjects = Subject.query.filter_by(teacher_id=int(teacher_id)).order_by(Subject.name).all()
    return jsonify([s.to_dict() for s in subjects]), 200


@subjects_bp.route("", methods=["POST"])
@jwt_required()
def create_subject():
    teacher_id = get_jwt_identity()
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    # Prevent duplicates for same teacher
    existing = Subject.query.filter_by(teacher_id=int(teacher_id), name=name).first()
    if existing:
        return jsonify(existing.to_dict()), 200

    subject = Subject(teacher_id=int(teacher_id), name=name)
    db.session.add(subject)
    db.session.commit()
    return jsonify(subject.to_dict()), 201
