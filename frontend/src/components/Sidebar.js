import React from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import '../styles/Sidebar.css';

function Sidebar({ isOpen, toggleSidebar }) {
    const navigate = useNavigate();
    const location = useLocation();
    const user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;

    if (!user) {
        return null;
    }

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const isActive = (path) => {
        return location.pathname === path;
    };

    const studentLinks = [
        { path: '/about', icon: 'ℹ️', label: 'About' },
        { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
        { path: '/catalog', icon: '📖', label: 'Book Catalog' },
        { path: '/requests', icon: '📋', label: 'My Requests' },
        { path: '/notifications', icon: '🔔', label: 'Notifications' },
        { path: '/profile', icon: '👤', label: 'Profile' },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
    ];

    const staffLinks = [
        { path: '/about', icon: 'ℹ️', label: 'About' },
        { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
        { path: '/book-management', icon: '📚', label: 'Manage Books' },
        { path: '/request-management', icon: '📋', label: 'Manage Requests' },
        { path: '/student-management', icon: '🎓', label: 'Manage Students' },
        { path: '/staff-management', icon: '👥', label: 'Add Staff' },
        { path: '/notifications', icon: '🔔', label: 'Notifications' },
        { path: '/profile', icon: '👤', label: 'Profile' },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
    ];

    const navLinks = user.role === 'staff' ? staffLinks : studentLinks;

    return (
        <>
            <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div className="sidebar-brand">
                        {isOpen && <span className="brand-text">Instant Library</span>}
                    </div>
                    <button
                        className="sidebar-toggle"
                        onClick={toggleSidebar}
                        style={{ position: 'static', transform: 'none', margin: 0 }}
                    >
                        {isOpen ? '«' : '☰'}
                    </button>
                </div>

                <nav className="sidebar-nav">
                    {navLinks.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
                            title={!isOpen ? link.label : ''}
                        >
                            <span className="nav-icon">{link.icon}</span>
                            {isOpen && <span className="nav-label">{link.label}</span>}
                        </Link>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="user-info">
                        {isOpen && (
                            <>
                                <div className="user-name">{user.name}</div>
                                <div className="user-role">
                                    {user.role === 'staff' ? '👤 Staff' : '🎓 Student'}
                                </div>
                            </>
                        )}
                    </div>
                    <button onClick={handleLogout} className="logout-btn" title={!isOpen ? 'Logout' : ''}>
                        <span className="logout-icon">🚪</span>
                        {isOpen && <span className="logout-text">Logout</span>}
                    </button>
                </div>
            </aside>

            <div className={`sidebar-overlay ${isOpen ? 'visible' : ''}`} onClick={toggleSidebar}></div>
        </>
    );
}

export default Sidebar;
