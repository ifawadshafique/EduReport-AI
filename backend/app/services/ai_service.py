import os
import json
from groq import Groq
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.assessment import Assessment
from app.models.topic import Topic

# We will instantiate the client lazily to ensure GROQ_API_KEY is loaded from .env
_client = None

def get_groq_client():
    global _client
    if not _client:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing")
        _client = Groq(api_key=api_key)
    return _client

def generate_full_report(student_id):
    """
    Gather all student data and prompt Groq's Llama 3 to generate a 6-section JSON report.
    Returns a dictionary with exactly 6 keys:
    overall_summary, academic_performance, attendance_and_participation, topics_covered, strengths_and_weaknesses, next_steps
    """
    client = get_groq_client()
    student = Student.query.get(student_id)
    if not student:
        raise ValueError("Student not found")

    stats = Student.bulk_stats([student.id]).get(student.id, {})
    att_pct = stats.get("attendance_percentage", "N/A")
    avg_score = stats.get("average_score", "N/A")

    assessments = Assessment.query.filter_by(student_id=student.id).all()
    topics = Topic.query.filter_by(student_id=student.id).all()

    # Compile the prompt
    data_context = f"""
STUDENT DATA FOR REPORT GENERATION:
Name: {student.full_name}
Grade: {student.grade or 'Not specified'}
Attendance: {att_pct}%
Average Score: {avg_score}%

TEACHER NOTES:
Strengths: {student.strengths or 'None noted'}
Weaknesses: {student.weaknesses or 'None noted'}
General Notes: {student.notes or 'None noted'}

ASSESSMENTS LOG:
"""
    for a in assessments:
        data_context += f"- {a.name} ({a.type}): {a.obtained_marks}/{a.max_marks} ({a.percentage}%)\n"
    if not assessments:
        data_context += "No assessments recorded yet.\n"

    data_context += "\nTOPICS LOG:\n"
    for t in topics:
        data_context += f"- {t.name} (Status: {t.status})\n"
    if not topics:
        data_context += "No topics recorded yet.\n"

    prompt = f"""
You are an expert, professional teacher writing a term progress report for a student.
Use the following raw student data to generate a high-quality, encouraging, but honest report.

{data_context}

You MUST output your response in JSON format. The JSON object MUST contain exactly these 6 string keys, containing the text for each section:
1. "overall_summary": A high-level overview of the student's progress.
2. "academic_performance": Detail regarding their assessment scores and understanding.
3. "attendance_and_participation": Commentary on their attendance and engagement.
4. "topics_covered": A summary of the topics they have learned and their mastery.
5. "strengths_and_weaknesses": Honest review of what they excel at and where they need support.
6. "next_steps": Actionable advice or goals for the next term.

Return STRICTLY valid JSON only. Keep the tone professional, objective, and supportive. Use paragraphs (\\n\\n) for readability within the string values.
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that outputs only valid JSON.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="mixtral-8x7b-32768",
        response_format={"type": "json_object"},
        temperature=0.4,
    )

    response_content = chat_completion.choices[0].message.content
    try:
        report_data = json.loads(response_content)
        # Ensure fallback for missing keys
        return {
            "overall_summary": report_data.get("overall_summary", ""),
            "academic_performance": report_data.get("academic_performance", ""),
            "attendance_and_participation": report_data.get("attendance_and_participation", ""),
            "topics_covered": report_data.get("topics_covered", ""),
            "strengths_and_weaknesses": report_data.get("strengths_and_weaknesses", ""),
            "next_steps": report_data.get("next_steps", "")
        }
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid JSON response")

