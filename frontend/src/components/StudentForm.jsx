import { useState } from "react";
import { api } from "../api/client";
import "../styles/modal.css";

const EMPTY = {
  first_name: "", last_name: "", grade: "",
  parent_name: "", parent_email: "",
  notes: "", strengths: "", weaknesses: "",
};

export default function StudentForm({ student, onClose, onSaved }) {
  const [form, setForm] = useState(student ? {
    first_name: student.first_name || "",
    last_name: student.last_name || "",
    grade: student.grade || "",
    parent_name: student.parent_name || "",
    parent_email: student.parent_email || "",
    notes: student.notes || "",
    strengths: student.strengths || "",
    weaknesses: student.weaknesses || "",
    status: student.status || "active",
  } : EMPTY);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (student) {
        await api.updateStudent(student.id, form);
      } else {
        await api.createStudent(form);
      }
      onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div className="modal-header">
          <h3>{student ? "Edit Student" : "Add Student"}</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={submit} className="modal-form">
          <div className="form-row">
            <div className="field">
              <label>First Name *</label>
              <input name="first_name" value={form.first_name} onChange={handle} required placeholder="Ahmed" />
            </div>
            <div className="field">
              <label>Last Name *</label>
              <input name="last_name" value={form.last_name} onChange={handle} required placeholder="Khan" />
            </div>
          </div>
          <div className="field">
            <label>Grade / Class</label>
            <input name="grade" value={form.grade} onChange={handle} placeholder="e.g. Grade 8, Class 9A" />
          </div>
          <div className="form-row">
            <div className="field">
              <label>Parent Name</label>
              <input name="parent_name" value={form.parent_name} onChange={handle} placeholder="Mr. Khan" />
            </div>
            <div className="field">
              <label>Parent Email</label>
              <input name="parent_email" type="email" value={form.parent_email} onChange={handle} placeholder="parent@email.com" />
            </div>
          </div>
          <div className="field">
            <label>Strengths</label>
            <textarea name="strengths" value={form.strengths} onChange={handle} rows={2} placeholder="e.g. excellent at problem-solving, participates actively" />
          </div>
          <div className="field">
            <label>Areas for Improvement</label>
            <textarea name="weaknesses" value={form.weaknesses} onChange={handle} rows={2} placeholder="e.g. needs more practice with written work" />
          </div>
          <div className="field">
            <label>Teacher Notes</label>
            <textarea name="notes" value={form.notes} onChange={handle} rows={2} placeholder="Any general notes about the student" />
          </div>
          {student && (
            <div className="field">
              <label>Status</label>
              <select name="status" value={form.status} onChange={handle}>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          )}
          {error && <p className="auth-error">{error}</p>}
          <div className="modal-actions">
            <button type="button" className="btn-outline" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Saving…" : student ? "Save Changes" : "Add Student"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
