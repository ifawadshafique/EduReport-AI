from app import db
from datetime import datetime, timezone
from sqlalchemy import func, case


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(50), nullable=True)
    parent_name = db.Column(db.String(120), nullable=True)
    parent_email = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default="active")  # active / archived
    notes = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    teacher = db.relationship("User", back_populates="students")
    attendance_records = db.relationship("Attendance", back_populates="student", lazy=True, cascade="all, delete-orphan")
    assessments = db.relationship("Assessment", back_populates="student", lazy=True, cascade="all, delete-orphan")
    topics = db.relationship("Topic", back_populates="student", lazy=True, cascade="all, delete-orphan")
    reports = db.relationship("Report", back_populates="student", lazy=True, cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # ------------------------------------------------------------------
    # Single-student stat properties (fine for StudentDetail / one-off use).
    # Do NOT call these in a loop over many students — use bulk_stats() instead.
    # ------------------------------------------------------------------
    @property
    def attendance_percentage(self):
        from app.models.attendance import Attendance
        stats = Student.bulk_stats([self.id])
        return stats.get(self.id, {}).get("attendance_percentage")

    @property
    def average_score(self):
        from app.models.assessment import Assessment
        stats = Student.bulk_stats([self.id])
        return stats.get(self.id, {}).get("average_score")

    @classmethod
    def bulk_stats(cls, student_ids: list) -> dict:
        """Return {student_id: {attendance_percentage, average_score}} for all
        supplied IDs using exactly 2 aggregate SQL queries — O(1) queries
        regardless of the number of students."""
        if not student_ids:
            return {}

        from app.models.attendance import Attendance
        from app.models.assessment import Assessment

        # --- Attendance: COUNT(total) and COUNT(present/late) per student ---
        att_rows = (
            db.session.query(
                Attendance.student_id,
                func.count(Attendance.id).label("total"),
                func.sum(
                    case(
                        (Attendance.status.in_(["present", "late"]), 1),
                        else_=0,
                    )
                ).label("attended"),
            )
            .filter(Attendance.student_id.in_(student_ids))
            .group_by(Attendance.student_id)
            .all()
        )
        att_map = {
            row.student_id: round(row.attended / row.total * 100, 1)
            if row.total else None
            for row in att_rows
        }

        # --- Assessments: weighted average score per student ---
        score_rows = (
            db.session.query(
                Assessment.student_id,
                func.sum(Assessment.obtained_marks).label("obtained"),
                func.sum(Assessment.max_marks).label("maximum"),
            )
            .filter(
                Assessment.student_id.in_(student_ids),
                Assessment.max_marks > 0,
            )
            .group_by(Assessment.student_id)
            .all()
        )
        score_map = {
            row.student_id: round(row.obtained / row.maximum * 100, 1)
            if row.maximum else None
            for row in score_rows
        }

        return {
            sid: {
                "attendance_percentage": att_map.get(sid),
                "average_score": score_map.get(sid),
            }
            for sid in student_ids
        }

    def to_dict(self, include_stats=False):
        data = {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "grade": self.grade,
            "parent_name": self.parent_name,
            "parent_email": self.parent_email,
            "status": self.status,
            "notes": self.notes,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "created_at": self.created_at.isoformat(),
        }
        if include_stats:
            # Caller should inject these from bulk_stats() rather than
            # letting the properties re-query individually.
            data["attendance_percentage"] = self.attendance_percentage
            data["average_score"] = self.average_score
        return data

    def to_dict_with_stats(self, stats: dict):
        """to_dict() but uses pre-fetched stats dict from bulk_stats()."""
        data = self.to_dict(include_stats=False)
        data["attendance_percentage"] = stats.get("attendance_percentage")
        data["average_score"] = stats.get("average_score")
        return data
