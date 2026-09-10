from app import db
from datetime import datetime, timezone


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), default="quiz")
    # type: quiz / test / assignment / project / exam / homework
    max_marks = db.Column(db.Float, nullable=False, default=100)
    obtained_marks = db.Column(db.Float, nullable=False, default=0)
    date = db.Column(db.Date, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship("Student", back_populates="assessments")

    @property
    def percentage(self):
        if self.max_marks and self.max_marks > 0:
            return round(self.obtained_marks / self.max_marks * 100, 1)
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "name": self.name,
            "type": self.type,
            "max_marks": self.max_marks,
            "obtained_marks": self.obtained_marks,
            "percentage": self.percentage,
            "date": self.date.isoformat() if self.date else None,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
