from app import db
from datetime import datetime, timezone


class Attendance(db.Model):
    __tablename__ = "attendance"

    # Prevent logging the same student twice on the same date at the DB level
    __table_args__ = (
        db.UniqueConstraint("student_id", "date", name="uq_attendance_student_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="present")
    # status: present / absent / late / excused

    student = db.relationship("Student", back_populates="attendance_records")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "date": self.date.isoformat(),
            "status": self.status,
        }
