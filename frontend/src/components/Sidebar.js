import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/Sidebar.css';

function Sidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const [isOpen, setIsOpen] = useState(true);
    const user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;

    if (!user) {
        return null;
    }

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const toggleSidebar = () => {
        setIsOpen(!isOpen);
    };

    const isActive = (path) => {
        return location.pathname === path;
    };

    const studentLinks = [
        { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
        { path: '/catalog', icon: '📖', label: 'Book Catalog' },
        { path: '/requests', icon: '📋', label: 'My Requests' },
        { path: '/profile', icon: '👤', label: 'Profile' },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
    ];

    const staffLinks = [
        { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
        { path: '/book-management', icon: '📚', label: 'Manage Books' },
        { path: '/request-management', icon: '📋', label: 'Manage Requests' },
        { path: '/staff-management', icon: '👥', label: 'Add Staff' },
        { path: '/profile', icon: '👤', label: 'Profile' },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
    ];

    const navLinks = user.role === 'staff' ? staffLinks : studentLinks;

    return (
        <>
            <button className="sidebar-toggle" onClick={toggleSidebar}>
                {isOpen ? '◀' : '▶'}
            </button>

            <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <div className="sidebar-brand">
                        <span className="brand-icon">📚</span>
                        {isOpen && <span className="brand-text">Instant Library</span>}
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {navLinks.map((link) => (
                        <a
                            key={link.path}
                            href={link.path}
                            className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
                            title={!isOpen ? link.label : ''}
                        >
                            <span className="nav-icon">{link.icon}</span>
                            {isOpen && <span className="nav-label">{link.label}</span>}
                        </a>
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
