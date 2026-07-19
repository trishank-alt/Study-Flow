import { NavLink, useLocation } from 'react-router-dom';
import './Sidebar.css';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/subjects', label: 'Subjects', icon: '📚' },
  { path: '/resources', label: 'Resources', icon: '📁' },
  { path: '/exams', label: 'Exams', icon: '📝' },
  { path: '/planner', label: 'Planner', icon: '📅' },
  { path: '/settings', label: 'Settings', icon: '⚙️' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">🎓</span>
          <span className="logo-text">StudyPlanner</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={`sidebar-link ${location.pathname === item.path || location.pathname.startsWith(item.path + '/') ? 'active' : ''}`}
          >
            <span className="sidebar-link-icon">{item.icon}</span>
            <span className="sidebar-link-label">{item.label}</span>
            {(location.pathname === item.path || location.pathname.startsWith(item.path + '/')) && (
              <div className="sidebar-active-indicator" />
            )}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-version">MVP v1.0</div>
      </div>
    </aside>
  );
}
