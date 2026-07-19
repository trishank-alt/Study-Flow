import { useAuth } from '../../features/auth/AuthContext';
import './Navbar.css';

interface NavbarProps {
  title?: string;
}

export default function Navbar({ title }: NavbarProps) {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-left">
        <h2 className="navbar-title">{title || 'Dashboard'}</h2>
      </div>

      <div className="navbar-right">
        <div className="navbar-user">
          <div className="navbar-avatar">
            {user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
          <span className="navbar-email">{user?.email}</span>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={logout} id="logout-btn">
          Logout
        </button>
      </div>
    </header>
  );
}
