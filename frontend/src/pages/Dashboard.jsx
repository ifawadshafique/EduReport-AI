import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import Navbar from "../components/Navbar";
import "../styles/dashboard.css";

export default function Dashboard() {
  const [stats, setStats] = useState({ students: 0, reports: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    api.getStudents().then((students) => {
      setStats({ students: students.filter((s) => s.status === "active").length, reports: 0 });
    }).catch(() => {});
  }, []);

  return (
    <div className="page">
      <Navbar />
      <div className="container">
        <div className="dashboard-hero">
          <h2>Welcome back 👋</h2>
          <p>Track your students, generate AI-powered reports, and share them with parents.</p>
        </div>

        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-card-icon">🎓</div>
            <div className="stat-card-num">{stats.students}</div>
            <div className="stat-card-label">Active Students</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-icon">📄</div>
            <div className="stat-card-num">{stats.reports}</div>
            <div className="stat-card-label">Reports Generated</div>
          </div>
        </div>

        <div className="quick-actions">
          <h3>Quick Actions</h3>
          <div className="actions-row">
            <button className="action-card" onClick={() => navigate("/students")}>
              <span className="action-icon">➕</span>
              <span>Add a Student</span>
            </button>
            <button className="action-card" onClick={() => navigate("/students")}>
              <span className="action-icon">📋</span>
              <span>View All Students</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
