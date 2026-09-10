from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.topic import Topic
from app.utils import get_student_or_404
import datetime

topics_bp = Blueprint("topics", __name__)

VALID_STATUSES = ("not_started", "in_progress", "completed", "needs_revision")


@topics_bp.route("/api/students/<int:student_id>/topics", methods=["GET"])
@jwt_required()
def list_topics(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    records = (
        Topic.query.filter_by(student_id=student_id)
        .order_by(Topic.date_taught.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in records]), 200


@topics_bp.route("/api/students/<int:student_id>/topics", methods=["POST"])
@jwt_required()
def add_topic(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    status = data.get("status", "not_started")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

    date_taught = None
    if data.get("date_taught"):
        try:
            date_taught = datetime.date.fromisoformat(data["date_taught"])
        except ValueError:
            return jsonify({"error": "Invalid date_taught format, use YYYY-MM-DD"}), 400

    topic = Topic(
        student_id=student_id,
        subject_id=data.get("subject_id") or None,
        name=name,
        status=status,
        date_taught=date_taught,
    )
    db.session.add(topic)
    db.session.commit()
    return jsonify(topic.to_dict()), 201


@topics_bp.route("/api/students/<int:student_id>/topics/<int:topic_id>", methods=["PUT"])
@jwt_required()
def update_topic(student_id, topic_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    topic = Topic.query.filter_by(id=topic_id, student_id=student_id).first()
    if not topic:
        return jsonify({"error": "Topic not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        topic.name = data["name"].strip() or topic.name
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400
        topic.status = data["status"]
    if "date_taught" in data:
        try:
            topic.date_taught = datetime.date.fromisoformat(data["date_taught"]) if data["date_taught"] else None
        except ValueError:
            return jsonify({"error": "Invalid date_taught format"}), 400
    if "subject_id" in data:
        topic.subject_id = data["subject_id"] or None

    db.session.commit()
    return jsonify(topic.to_dict()), 200


@topics_bp.route("/api/students/<int:student_id>/topics/<int:topic_id>", methods=["DELETE"])
@jwt_required()
def delete_topic(student_id, topic_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    topic = Topic.query.filter_by(id=topic_id, student_id=student_id).first()
    if not topic:
        return jsonify({"error": "Topic not found"}), 404

    db.session.delete(topic)
    db.session.commit()
    return jsonify({"message": "Topic deleted"}), 200
