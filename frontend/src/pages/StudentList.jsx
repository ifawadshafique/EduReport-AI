import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import Navbar from "../components/Navbar";
import StudentForm from "../components/StudentForm";
import "../styles/students.css";

export default function StudentList() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editStudent, setEditStudent] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = async () => {
    try {
      const data = await api.getStudents();
      setStudents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleSaved = () => {
    setShowForm(false);
    setEditStudent(null);
    load();
  };

  const handleDelete = async () => {
    try {
      await api.deleteStudent(deleteTarget.id);
      setDeleteTarget(null);
      load();
    } catch (err) {
      alert(err.message);
    }
  };

  const active = students.filter((s) => s.status === "active");
  const archived = students.filter((s) => s.status === "archived");

  return (
    <div className="page">
      <Navbar />
      <div className="container">
        <div className="page-header">
          <div>
            <h2>Students</h2>
            <p className="page-sub">{active.length} active student{active.length !== 1 ? "s" : ""}</p>
          </div>
          <button className="btn-primary" onClick={() => { setEditStudent(null); setShowForm(true); }}>
            + Add Student
          </button>
        </div>

        {error && <p className="error-msg">{error}</p>}

        {loading ? (
          <div className="loading-state">Loading students…</div>
        ) : students.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🎓</div>
            <h3>No students yet</h3>
            <p>Add your first student to get started.</p>
            <button className="btn-primary" onClick={() => setShowForm(true)}>Add Student</button>
          </div>
        ) : (
          <>
            <div className="students-grid">
              {active.map((s) => (
                <div key={s.id} className="student-card">
                  <div className="student-card-header">
                    <div className="student-avatar">{s.first_name[0]}{s.last_name[0]}</div>
                    <div>
                      <h3>{s.full_name}</h3>
                      {s.grade && <span className="badge-grade">{s.grade}</span>}
                    </div>
                  </div>
                  <div className="student-stats">
                    <div className="stat">
                      <span className="stat-label">Attendance</span>
                      <span className="stat-value">
                        {s.attendance_percentage != null ? `${s.attendance_percentage}%` : "—"}
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Avg Score</span>
                      <span className="stat-value">
                        {s.average_score != null ? `${s.average_score}%` : "—"}
                      </span>
                    </div>
                  </div>
                  <div className="student-card-actions">
                    <Link to={`/students/${s.id}`} className="btn-outline">View</Link>
                    <button className="btn-ghost" onClick={() => { setEditStudent(s); setShowForm(true); }}>Edit</button>
                    <button className="btn-danger-ghost" onClick={() => setDeleteTarget(s)}>Delete</button>
                  </div>
                </div>
              ))}
            </div>

            {archived.length > 0 && (
              <details className="archived-section">
                <summary>Archived ({archived.length})</summary>
                <div className="students-grid mt-2">
                  {archived.map((s) => (
                    <div key={s.id} className="student-card archived">
                      <div className="student-card-header">
                        <div className="student-avatar muted">{s.first_name[0]}{s.last_name[0]}</div>
                        <div><h3>{s.full_name}</h3><span className="badge-archived">Archived</span></div>
                      </div>
                      <div className="student-card-actions">
                        <Link to={`/students/${s.id}`} className="btn-outline">View</Link>
                        <button className="btn-ghost" onClick={() => { setEditStudent(s); setShowForm(true); }}>Edit</button>
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </>
        )}
      </div>

      {showForm && (
        <StudentForm
          student={editStudent}
          onClose={() => { setShowForm(false); setEditStudent(null); }}
          onSaved={handleSaved}
        />
      )}

      {deleteTarget && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>Delete {deleteTarget.full_name}?</h3>
            <p>This will permanently delete the student and all their records.</p>
            <div className="modal-actions">
              <button className="btn-outline" onClick={() => setDeleteTarget(null)}>Cancel</button>
              <button className="btn-danger" onClick={handleDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
