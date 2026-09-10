# EduReport AI

AI-powered student progress report generator for teachers.

## Quick Start

### Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
# Copy .env.example to .env and fill in your GROQ_API_KEY when ready
copy .env.example .env
python run.py
```

Backend runs on: **http://localhost:5000**
Health check: **http://localhost:5000/api/health**

---

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173**

---

## Build Progress

| Step | Feature                                      | Status     |
| ---- | -------------------------------------------- | ---------- |
| 1    | Skeleton (Flask + Vite)                      | ✅ Done    |
| 2    | Auth + Student CRUD                          | 🔲 Pending |
| 3    | Data Entry (Attendance, Assessments, Topics) | 🔲 Pending |
| 4    | AI Report Generation                         | 🔲 Pending |
| 5    | PDF Export + History                         | 🔲 Pending |

## Tech Stack

- **Frontend**: React (Vite), React Router
- **Backend**: Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Database**: SQLite (dev) → PostgreSQL (prod, config change only)
- **AI**: Groq API (llama-3.1-8b-instant)
- **PDF**: pdfkit + wkhtmltopdf
