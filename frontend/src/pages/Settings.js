import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function Settings() {
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
            <Breadcrumb pageTitle="Settings" />
            <div className="settings-container">
                <div className="settings-content">
                    <div className="settings-card">
                        <h1>Settings - Coming Soon</h1>
                        <p>This section will include preferences, notifications, and account settings.</p>
                        <div className="settings-preview">
                            <div className="setting-item">
                                <h3>🔔 Notifications</h3>
                                <p>Manage notification preferences and alerts</p>
                            </div>
                            <div className="setting-item">
                                <h3>🎨 Appearance</h3>
                                <p>Customize theme and display settings</p>
                            </div>
                            <div className="setting-item">
                                <h3>🔒 Privacy & Security</h3>
                                <p>Control privacy settings and security options</p>
                            </div>
                            <div className="setting-item">
                                <h3>⚙️ General</h3>
                                <p>General account and system settings</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default Settings;
