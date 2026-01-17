import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function Dashboard() {
    const navigate = useNavigate();

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        }
    }, [navigate]);

    const user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;

    if (!user) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <>
            <Breadcrumb pageTitle="Overview" />
            <div className="dashboard-container">
                <div className="dashboard-content">
                    <div className="welcome-section">
                        <h1>Welcome, {user.name}!</h1>
                        <p>Email: {user.email}</p>
                        <p>Role: <strong>{user.role === 'student' ? 'Student' : 'Staff'}</strong></p>
                        <p className="subtitle">You have successfully logged in to Instant Library</p>
                    </div>


                    {user.role === 'staff' && (
                        <div className="staff-panel">
                            <h2>Staff Operations</h2>
                            <div className="staff-actions">
                                <a href="/book-management" className="staff-action-btn">
                                    <span className="icon">📚</span>
                                    <span className="label">Manage Books</span>
                                </a>
                                <a href="/request-management" className="staff-action-btn">
                                    <span className="icon">📋</span>
                                    <span className="label">Manage Requests</span>
                                </a>
                                <a href="/staff-management" className="staff-action-btn">
                                    <span className="icon">👥</span>
                                    <span className="label">Add Staff Member</span>
                                </a>
                            </div>
                        </div>
                    )}

                    {user.role === 'student' && (
                        <div className="student-quick-actions">
                            <h2>Quick Actions</h2>
                            <div className="quick-actions">
                                <a href="/catalog" className="quick-action-btn">
                                    <span className="icon">📖</span>
                                    <span className="label">Browse Books</span>
                                </a>
                                <a href="/requests" className="quick-action-btn">
                                    <span className="icon">📋</span>
                                    <span className="label">My Requests</span>
                                </a>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

export default Dashboard;
