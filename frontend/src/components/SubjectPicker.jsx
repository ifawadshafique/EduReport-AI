import { useState, useEffect } from "react";
import { api } from "../api/client";
import "../styles/modal.css";

/**
 * A subject selector that:
 * - Shows a dropdown of existing subjects
 * - Lets the teacher create a new subject inline if none exist or they want a new one
 * - Always returns subject_id or null (never blocks the form)
 */
export default function SubjectPicker({ value, onChange }) {
  const [subjects, setSubjects] = useState([]);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getSubjects().then(setSubjects).catch(() => {});
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setLoading(true);
    try {
      const subject = await api.createSubject({ name: newName.trim() });
      setSubjects((prev) => [...prev, subject]);
      onChange(subject.id);
      setCreating(false);
      setNewName("");
    } catch {
      /* ignore duplicate — server returns the existing one */
    } finally {
      setLoading(false);
    }
  };

  if (creating) {
    return (
      <div style={{ display: "flex", gap: ".5rem" }}>
        <input
          autoFocus
          placeholder="New subject name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          style={{ flex: 1, border: "1.5px solid var(--border)", borderRadius: 8, padding: ".5rem .75rem" }}
        />
        <button type="button" className="btn-primary" onClick={handleCreate} disabled={loading}>
          {loading ? "…" : "Add"}
        </button>
        <button type="button" className="btn-ghost" onClick={() => setCreating(false)}>Cancel</button>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", gap: ".5rem", alignItems: "center" }}>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value ? parseInt(e.target.value) : null)}
        style={{ flex: 1, border: "1.5px solid var(--border)", borderRadius: 8, padding: ".5rem .75rem", background: "var(--surface)" }}
      >
        <option value="">— No subject —</option>
        {subjects.map((s) => (
          <option key={s.id} value={s.id}>{s.name}</option>
        ))}
      </select>
      <button type="button" className="btn-ghost" onClick={() => setCreating(true)} title="Add new subject">+ New</button>
    </div>
  );
}
