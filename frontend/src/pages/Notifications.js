import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function Notifications() {
    const navigate = useNavigate();

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    return (
        <>
            <Breadcrumb pageTitle="Notifications" />
            <div className="notifications-container">
                <div className="notifications-content">
                    <div className="notifications-card">
                        <h1>Notifications - Coming Soon</h1>
                        <p>Stay updated with notifications about your book requests and library activities.</p>
                        <div className="notifications-preview">
                            <div className="notification-item">
                                <span className="notification-icon">📬</span>
                                <h3>System Notifications</h3>
                                <p>Important updates and announcements</p>
                            </div>
                            <div className="notification-item">
                                <span className="notification-icon">📖</span>
                                <h3>Book Updates</h3>
                                <p>Updates about your requested books</p>
                            </div>
                            <div className="notification-item">
                                <span className="notification-icon">⏰</span>
                                <h3>Reminders</h3>
                                <p>Return date reminders and due notices</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default Notifications;
