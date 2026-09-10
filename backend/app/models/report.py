from app import db
from datetime import datetime, timezone


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    period_label = db.Column(db.String(100), nullable=False)  # e.g. "September 2026"
    status = db.Column(db.String(20), default="draft")  # draft / approved
    content_json = db.Column(db.JSON, nullable=True)
    ai_provider = db.Column(db.String(50), nullable=True)
    
    # The 6 configurable sections of the report
    overall_summary = db.Column(db.Text, nullable=True)
    academic_performance = db.Column(db.Text, nullable=True)
    attendance_and_participation = db.Column(db.Text, nullable=True)
    topics_covered = db.Column(db.Text, nullable=True)
    strengths_and_weaknesses = db.Column(db.Text, nullable=True)
    next_steps = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    student = db.relationship("Student", back_populates="reports")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "teacher_id": self.teacher_id,
            "period_label": self.period_label,
            "status": self.status,
            "content_json": self.content_json,
            "ai_provider": self.ai_provider,
            "overall_summary": self.overall_summary,
            "academic_performance": self.academic_performance,
            "attendance_and_participation": self.attendance_and_participation,
            "topics_covered": self.topics_covered,
            "strengths_and_weaknesses": self.strengths_and_weaknesses,
            "next_steps": self.next_steps,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
