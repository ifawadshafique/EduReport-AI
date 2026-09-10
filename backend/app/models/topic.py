from app import db
from datetime import datetime, timezone


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), default="not_started")
    # status: not_started / in_progress / completed / needs_revision
    date_taught = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship("Student", back_populates="topics")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "name": self.name,
            "status": self.status,
            "date_taught": self.date_taught.isoformat() if self.date_taught else None,
            "created_at": self.created_at.isoformat(),
        }
