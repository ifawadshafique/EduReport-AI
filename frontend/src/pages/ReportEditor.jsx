import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";
import Navbar from "../components/Navbar";

export default function ReportEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    try {
      const rep = await api.getReport(id);
      setReport(rep);
      const stu = await api.getStudent(rep.student_id);
      setStudent(stu);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { loadData(); }, [loadData]);

  const save = async () => {
    setSaving(true);
    try {
      await api.updateReport(id, report);
      alert("Report saved successfully!");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const updateSection = (key, value) => {
    setReport({ ...report, [key]: value });
  };

  if (loading) return <div className="page"><Navbar /><div className="container loading-state">Loading AI Report…</div></div>;
  if (!report) return <div className="page"><Navbar /><div className="container"><p className="inline-error">{error || "Report not found"}</p></div></div>;

  return (
    <div className="page" style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />
      
      <div className="detail-header" style={{ padding: "1rem 2rem", background: "var(--surface)", borderBottom: "1px solid var(--border)", marginBottom: 0 }}>
        <div>
          <Link to={`/students/${report.student_id}`} className="back-link">← Back to Student</Link>
          <h2 style={{ margin: 0 }}>Report Editor: {student?.full_name}</h2>
        </div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          {error && <span className="inline-error" style={{ margin: 0 }}>{error}</span>}
          <button className="btn-primary" onClick={save} disabled={saving}>
            {saving ? "Saving…" : "💾 Save Report"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        
        {/* Editor Pane (Left) */}
        <div style={{ flex: 2, overflowY: "auto", padding: "2rem", background: "var(--bg)" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", maxWidth: "800px", margin: "0 auto" }}>
            
            <div className="section-card">
              <h4>Overall Summary</h4>
              <textarea rows={5} value={report.overall_summary || ""} onChange={(e) => updateSection("overall_summary", e.target.value)} />
            </div>

            <div className="section-card">
              <h4>Academic Performance</h4>
              <textarea rows={5} value={report.academic_performance || ""} onChange={(e) => updateSection("academic_performance", e.target.value)} />
            </div>

            <div className="section-card">
              <h4>Attendance & Participation</h4>
              <textarea rows={4} value={report.attendance_and_participation || ""} onChange={(e) => updateSection("attendance_and_participation", e.target.value)} />
            </div>

            <div className="section-card">
              <h4>Topics Covered</h4>
              <textarea rows={4} value={report.topics_covered || ""} onChange={(e) => updateSection("topics_covered", e.target.value)} />
            </div>

            <div className="section-card">
              <h4>Strengths & Weaknesses</h4>
              <textarea rows={4} value={report.strengths_and_weaknesses || ""} onChange={(e) => updateSection("strengths_and_weaknesses", e.target.value)} />
            </div>

            <div className="section-card">
              <h4>Next Steps</h4>
              <textarea rows={4} value={report.next_steps || ""} onChange={(e) => updateSection("next_steps", e.target.value)} />
            </div>

          </div>
        </div>

        {/* Reference Sidebar (Right) */}
        <div style={{ flex: 1, borderLeft: "1px solid var(--border)", background: "var(--surface)", padding: "2rem", overflowY: "auto" }}>
          <h3 style={{ marginTop: 0, color: "var(--text)", fontSize: "1.1rem" }}>Reference Data</h3>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "1.5rem" }}>
            The AI used this data to draft the report lengths. Use it to verify accuracy while editing.
          </p>

          <div style={{ marginBottom: "1.5rem" }}>
            <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)" }}>Stats</h4>
            <div style={{ background: "var(--bg)", padding: "1rem", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <p style={{ margin: "0 0 0.5rem" }}><strong>Attendance:</strong> {student?.attendance_percentage || "—"}%</p>
              <p style={{ margin: 0 }}><strong>Avg Score:</strong> {student?.average_score || "—"}%</p>
            </div>
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)" }}>Teacher Notes</h4>
            <div style={{ background: "var(--bg)", padding: "1rem", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem" }}><strong>Strengths:</strong> {student?.strengths || "None"}</p>
              <p style={{ margin: "0 0 0.5rem", fontSize: "0.9rem" }}><strong>Weaknesses:</strong> {student?.weaknesses || "None"}</p>
              <p style={{ margin: 0, fontSize: "0.9rem" }}><strong>Notes:</strong> {student?.notes || "None"}</p>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
