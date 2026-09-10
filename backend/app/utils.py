from app.models.student import Student


def get_student_or_404(student_id, teacher_id):
    """Fetch a student by ID and verify the requesting teacher owns it.

    Returns the Student object if found and owned, or None otherwise.
    Deliberately returns None (not raises) in both the "not found" and
    "found but belongs to another teacher" cases — callers return 404
    either way, so we never leak "this ID exists but isn't yours" to a
    probing client.
    """
    student = Student.query.get(student_id)
    if not student or student.teacher_id != int(teacher_id):
        return None
    return student
