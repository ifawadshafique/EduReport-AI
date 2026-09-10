from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.report import Report
from app.utils import get_student_or_404
from app.services.ai_service import generate_full_report

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/api/students/<int:student_id>/reports/generate", methods=["POST"])
@jwt_required()
def generate_report(student_id):
    teacher_id = get_jwt_identity()
    student = get_student_or_404(student_id, teacher_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    try:
        # Call the external Groq LLM service
        ai_data = generate_full_report(student_id)
    except Exception as e:
        return jsonify({"error": f"AI generation failed: {str(e)}"}), 500

    report = Report(
        student_id=student_id,
        ai_provider="groq-mixtral-8x7b",
        status="draft",
        overall_summary=ai_data.get("overall_summary", ""),
        academic_performance=ai_data.get("academic_performance", ""),
        attendance_and_participation=ai_data.get("attendance_and_participation", ""),
        topics_covered=ai_data.get("topics_covered", ""),
        strengths_and_weaknesses=ai_data.get("strengths_and_weaknesses", ""),
        next_steps=ai_data.get("next_steps", "")
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify(report.to_dict()), 201


@reports_bp.route("/api/reports/<int:report_id>", methods=["GET"])
@jwt_required()
def get_report(report_id):
    teacher_id = get_jwt_identity()
    report = Report.query.get(report_id)
    
    # Ownership verification via the associated student
    if not report or not get_student_or_404(report.student_id, teacher_id):
        return jsonify({"error": "Report not found"}), 404
        
    return jsonify(report.to_dict()), 200


@reports_bp.route("/api/reports/<int:report_id>", methods=["PUT"])
@jwt_required()
def update_report(report_id):
    teacher_id = get_jwt_identity()
    report = Report.query.get(report_id)
    
    if not report or not get_student_or_404(report.student_id, teacher_id):
        return jsonify({"error": "Report not found"}), 404

    data = request.get_json() or {}
    
    # Update the 6 sections
    editable_fields = [
        "overall_summary", "academic_performance", 
        "attendance_and_participation", "topics_covered", 
        "strengths_and_weaknesses", "next_steps", "status"
    ]
    
    for field in editable_fields:
        if field in data:
            setattr(report, field, data[field])
            
    db.session.commit()
    return jsonify(report.to_dict()), 200
