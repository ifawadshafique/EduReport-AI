import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/navbar.css";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span className="brand-icon">📋</span>
        <span>EduReport AI</span>
      </Link>
      <div className="navbar-links">
        <Link to="/" className="nav-link">Dashboard</Link>
        <Link to="/students" className="nav-link">Students</Link>
      </div>
      <div className="navbar-user">
        <span className="user-name">{user?.name}</span>
        <button className="btn-logout" onClick={handleLogout}>Log out</button>
      </div>
    </nav>
  );
}
