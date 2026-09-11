import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";
import Navbar from "../components/Navbar";
import SubjectPicker from "../components/SubjectPicker";
import "../styles/detail.css";

const TABS = ["Overview", "Attendance", "Assessments", "Topics", "Reports"];
const STATUS_COLORS = {
  present: "#22c55e", late: "#f59e0b", absent: "#ef4444", excused: "#8b5cf6",
};
const TOPIC_COLORS = {
  not_started: "#94a3b8", in_progress: "#3b82f6", completed: "#22c55e", needs_revision: "#f59e0b",
};

// ─── Overview Tab ─────────────────────────────────────────────────────────────
function OverviewTab({ student, onUpdate }) {
  const [form, setForm] = useState({
    strengths: student.strengths || "",
    weaknesses: student.weaknesses || "",
    notes: student.notes || "",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const save = async () => {
    setSaving(true);
    await api.updateStudent(student.id, form);
    setSaving(false);
    setSaved(true);
    onUpdate();
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="tab-content">
      <div className="stats-bar">
        <div className="stat-pill">
          <span>Attendance</span>
          <strong>{student.attendance_percentage != null ? `${student.attendance_percentage}%` : "—"}</strong>
        </div>
        <div className="stat-pill">
          <span>Avg Score</span>
          <strong>{student.average_score != null ? `${student.average_score}%` : "—"}</strong>
        </div>
        <div className="stat-pill">
          <span>Grade</span>
          <strong>{student.grade || "—"}</strong>
        </div>
        <div className="stat-pill">
          <span>Parent</span>
          <strong>{student.parent_name || "—"}</strong>
        </div>
      </div>

      <div className="section-card">
        <h4>Strengths</h4>
        <textarea rows={3} value={form.strengths} onChange={(e) => setForm({ ...form, strengths: e.target.value })} placeholder="e.g. excellent problem-solving, participates actively" />
      </div>
      <div className="section-card">
        <h4>Areas for Improvement</h4>
        <textarea rows={3} value={form.weaknesses} onChange={(e) => setForm({ ...form, weaknesses: e.target.value })} placeholder="e.g. needs more practice with written work" />
      </div>
      <div className="section-card">
        <h4>Teacher Notes</h4>
        <textarea rows={3} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Any notes about this student" />
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginTop: ".5rem" }}>
        <button className="btn-primary" onClick={save} disabled={saving}>
          {saving ? "Saving…" : "Save Notes"}
        </button>
        {saved && <span style={{ color: "#22c55e", fontSize: ".85rem" }}>✓ Saved</span>}
      </div>
    </div>
  );
}

// ─── Attendance Tab ────────────────────────────────────────────────────────────
function AttendanceTab({ studentId }) {
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState({ date: "", status: "present" });
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editStatus, setEditStatus] = useState("");

  const load = useCallback(async () => {
    const data = await api.getAttendance(studentId);
    setRecords(data);
  }, [studentId]);

  useEffect(() => { load(); }, [load]);

  const add = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.addAttendance(studentId, form);
      setForm({ date: "", status: "present" });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const saveEdit = async (id) => {
    await api.updateAttendance(studentId, id, { status: editStatus });
    setEditingId(null);
    load();
  };

  const remove = async (id) => {
    await api.deleteAttendance(studentId, id);
    load();
  };

  return (
    <div className="tab-content">
      <form className="inline-form" onSubmit={add}>
        <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
        <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
          <option value="present">Present</option>
          <option value="absent">Absent</option>
          <option value="late">Late</option>
          <option value="excused">Excused</option>
        </select>
        <button type="submit" className="btn-primary">Add</button>
      </form>
      {error && <p className="inline-error">{error}</p>}

      {records.length === 0 ? (
        <p className="empty-hint">No attendance records yet.</p>
      ) : (
        <table className="data-table">
          <thead><tr><th>Date</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td>{r.date}</td>
                <td>
                  {editingId === r.id ? (
                    <select value={editStatus} onChange={(e) => setEditStatus(e.target.value)}>
                      <option value="present">Present</option>
                      <option value="absent">Absent</option>
                      <option value="late">Late</option>
                      <option value="excused">Excused</option>
                    </select>
                  ) : (
                    <span className="status-badge" style={{ background: STATUS_COLORS[r.status] + "22", color: STATUS_COLORS[r.status] }}>
                      {r.status}
                    </span>
                  )}
                </td>
                <td className="row-actions">
                  {editingId === r.id ? (
                    <>
                      <button className="btn-primary" style={{ fontSize: ".8rem", padding: ".25rem .6rem" }} onClick={() => saveEdit(r.id)}>Save</button>
                      <button className="btn-ghost" onClick={() => setEditingId(null)}>Cancel</button>
                    </>
                  ) : (
                    <>
                      <button className="btn-ghost" onClick={() => { setEditingId(r.id); setEditStatus(r.status); }}>Edit</button>
                      <button className="btn-danger-ghost" onClick={() => remove(r.id)}>Delete</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ─── Assessments Tab ────────────────────────────────────────────────────────────
function AssessmentsTab({ studentId }) {
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState({ name: "", type: "quiz", subject_id: null, max_marks: 100, obtained_marks: "", date: "", comment: "" });
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    const data = await api.getAssessments(studentId);
    setRecords(data);
  }, [studentId]);

  useEffect(() => { load(); }, [load]);

  const add = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.addAssessment(studentId, form);
      setForm({ name: "", type: "quiz", subject_id: null, max_marks: 100, obtained_marks: "", date: "", comment: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const remove = async (id) => {
    await api.deleteAssessment(studentId, id);
    load();
  };

  return (
    <div className="tab-content">
      <form className="section-card" onSubmit={add}>
        <div className="form-row">
          <div className="field">
            <label>Assessment Name *</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Quiz 1" required />
          </div>
          <div className="field">
            <label>Type</label>
            <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
              {["quiz", "test", "assignment", "project", "exam", "homework"].map((t) => (
                <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Subject (optional)</label>
          <SubjectPicker value={form.subject_id} onChange={(id) => setForm({ ...form, subject_id: id })} />
        </div>
        <div className="form-row">
          <div className="field">
            <label>Max Marks</label>
            <input type="number" min="1" value={form.max_marks} onChange={(e) => setForm({ ...form, max_marks: e.target.value })} required />
          </div>
          <div className="field">
            <label>Obtained Marks</label>
            <input type="number" min="0" value={form.obtained_marks} onChange={(e) => setForm({ ...form, obtained_marks: e.target.value })} placeholder={`0–${form.max_marks}`} required />
          </div>
          <div className="field">
            <label>Date</label>
            <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
          </div>
        </div>
        <div className="field">
          <label>Comment</label>
          <input value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} placeholder="Optional note about this assessment" />
        </div>
        {error && <p className="inline-error">{error}</p>}
        <button type="submit" className="btn-primary">Add Assessment</button>
      </form>

      {records.length === 0 ? (
        <p className="empty-hint">No assessments yet.</p>
      ) : (
        <table className="data-table">
          <thead><tr><th>Name</th><th>Type</th><th>Score</th><th>%</th><th>Date</th><th></th></tr></thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td>{r.name}</td>
                <td><span className="type-badge">{r.type}</span></td>
                <td>{r.obtained_marks}/{r.max_marks}</td>
                <td>
                  <strong style={{ color: r.percentage >= 60 ? "#22c55e" : "#ef4444" }}>
                    {r.percentage}%
                  </strong>
                </td>
                <td>{r.date || "—"}</td>
                <td className="row-actions">
                  <button className="btn-danger-ghost" onClick={() => remove(r.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ─── Topics Tab ────────────────────────────────────────────────────────────────
function TopicsTab({ studentId }) {
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState({ name: "", subject_id: null, status: "not_started", date_taught: "" });
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    const data = await api.getTopics(studentId);
    setRecords(data);
  }, [studentId]);

  useEffect(() => { load(); }, [load]);

  const add = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.addTopic(studentId, form);
      setForm({ name: "", subject_id: null, status: "not_started", date_taught: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  const updateStatus = async (id, status) => {
    await api.updateTopic(studentId, id, { status });
    load();
  };

  const remove = async (id) => {
    await api.deleteTopic(studentId, id);
    load();
  };

  return (
    <div className="tab-content">
      <form className="section-card" onSubmit={add}>
        <div className="form-row">
          <div className="field" style={{ flex: 2 }}>
            <label>Topic Name *</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Variables and Data Types" required />
          </div>
          <div className="field">
            <label>Initial Status</label>
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="needs_revision">Needs Revision</option>
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="field">
            <label>Subject (optional)</label>
            <SubjectPicker value={form.subject_id} onChange={(id) => setForm({ ...form, subject_id: id })} />
          </div>
          <div className="field">
            <label>Date Taught</label>
            <input type="date" value={form.date_taught} onChange={(e) => setForm({ ...form, date_taught: e.target.value })} />
          </div>
        </div>
        {error && <p className="inline-error">{error}</p>}
        <button type="submit" className="btn-primary">Add Topic</button>
      </form>

      {records.length === 0 ? (
        <p className="empty-hint">No topics yet.</p>
      ) : (
        <table className="data-table">
          <thead><tr><th>Topic</th><th>Status</th><th>Date Taught</th><th></th></tr></thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td>{r.name}</td>
                <td>
                  <select
                    value={r.status}
                    onChange={(e) => updateStatus(r.id, e.target.value)}
                    className="status-select"
                    style={{ color: TOPIC_COLORS[r.status] }}
                  >
                    <option value="not_started">Not Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="needs_revision">Needs Revision</option>
                  </select>
                </td>
                <td>{r.date_taught || "—"}</td>
                <td className="row-actions">
                  <button className="btn-danger-ghost" onClick={() => remove(r.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ─── Reports Tab ────────────────────────────────────────────────────────────────
function ReportsTab({ studentId }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.getStudentReports(studentId);
      setReports(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="tab-content"><p>Loading reports...</p></div>;

  return (
    <div className="tab-content">
      {reports.length === 0 ? (
        <p className="empty-hint">No reports generated yet. Click "Generate AI Report" above to draft one.</p>
      ) : (
        <table className="data-table">
          <thead><tr><th>Period</th><th>Generated At</th><th>Status</th><th>Provider</th><th></th></tr></thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id}>
                <td>{r.period_label || "Unknown Term"}</td>
                <td>{new Date(r.created_at).toLocaleDateString()}</td>
                <td>
                  <span className="type-badge" style={{ background: r.status === 'draft' ? '#f59e0b22' : '#22c55e22', color: r.status === 'draft' ? '#f59e0b' : '#22c55e' }}>
                    {r.status}
                  </span>
                </td>
                <td style={{ fontSize: "0.85rem", color: "#64748b" }}>{r.ai_provider || "Legacy Model"}</td>
                <td className="row-actions">
                  <Link to={`/reports/${r.id}`} className="btn-primary" style={{ padding: "0.25rem 0.6rem", fontSize: "0.85rem", textDecoration: "none" }}>View / Edit</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function StudentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [tab, setTab] = useState("Overview");
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const loadStudent = useCallback(async () => {
    try {
      const s = await api.getStudent(id);
      setStudent(s);
    } catch {
      navigate("/students");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { loadStudent(); }, [loadStudent]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const rep = await api.generateReport(id);
      navigate(`/reports/${rep.id}`);
    } catch (e) {
      alert("Failed to generate report: " + e.message);
      setGenerating(false);
    }
  };

  if (loading) return <div className="page"><Navbar /><div className="container loading-state">Loading student data…</div></div>;
  if (!student) return null;

  return (
    <div className="page">
      <Navbar />
      <div className="container">
        <div className="detail-header">
          <div>
            <Link to="/students" className="back-link">← Students</Link>
            <h2>{student.full_name}</h2>
            {student.grade && <span className="badge-grade">{student.grade}</span>}
          </div>
          <button 
            className="btn-primary" 
            onClick={handleGenerateReport} 
            disabled={generating}
            style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
          >
            {generating ? "Generating..." : "✨ Generate AI Report"}
          </button>
        </div>

        <div className="tab-bar">
          {TABS.map((t) => (
            <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>{t}</button>
          ))}
        </div>

        {tab === "Overview" && <OverviewTab student={student} onUpdate={loadStudent} />}
        {tab === "Attendance" && <AttendanceTab studentId={parseInt(id)} />}
        {tab === "Assessments" && <AssessmentsTab studentId={parseInt(id)} />}
        {tab === "Topics" && <TopicsTab studentId={parseInt(id)} />}
        {tab === "Reports" && <ReportsTab studentId={parseInt(id)} />}
      </div>
    </div>
  );
}
