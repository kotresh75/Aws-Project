import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Settings() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('general');
    const [user, setUser] = useState(null);
    const [emailNotifs, setEmailNotifs] = useState(localStorage.getItem('emailNotifs') !== 'false');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            setUser(JSON.parse(userData));
        }
    }, [navigate]);

    const handleEmailNotifsToggle = () => {
        const newStatus = !emailNotifs;
        setEmailNotifs(newStatus);
        localStorage.setItem('emailNotifs', newStatus);
    };

    if (!user) return <div>Loading...</div>;

    const renderContent = () => {
        switch (activeTab) {
            case 'general':
                return (
                    <div>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: 'var(--text-main)', borderBottom: '1px solid rgba(255,255,255,0.4)', paddingBottom: '0.5rem' }}>⚙️ General Settings</h2>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Full Name</label>
                            <input type="text" value={user.name} disabled style={{ width: '100%', padding: '0.8rem', background: 'rgba(0,0,0,0.05)', border: 'none', borderRadius: '8px', color: 'var(--text-main)' }} />
                        </div>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Email Address</label>
                            <input type="text" value={user.email} disabled style={{ width: '100%', padding: '0.8rem', background: 'rgba(0,0,0,0.05)', border: 'none', borderRadius: '8px', color: 'var(--text-main)' }} />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Account Type</label>
                            <span className="badge badge-primary">{user.role}</span>
                        </div>
                    </div>
                );
            case 'notifications':
                return (
                    <div>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: 'var(--text-main)', borderBottom: '1px solid rgba(255,255,255,0.4)', paddingBottom: '0.5rem' }}>🔔 Notifications</h2>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 0', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>
                            <div>
                                <h4 style={{ margin: 0, color: 'var(--text-main)' }}>Email Notifications</h4>
                                <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)' }}>Receive updates about your book requests via email</p>
                            </div>
                            <label style={{ position: 'relative', display: 'inline-block', width: '50px', height: '26px' }}>
                                <input type="checkbox" checked={emailNotifs} onChange={handleEmailNotifsToggle} style={{ opacity: 0, width: 0, height: 0 }} />
                                <span style={{ position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: emailNotifs ? 'var(--primary)' : '#ccc', borderRadius: '34px', transition: '.4s' }}>
                                    <span style={{ position: 'absolute', content: "", height: '18px', width: '18px', left: '4px', bottom: '4px', backgroundColor: 'white', borderRadius: '50%', transition: '.4s', transform: emailNotifs ? 'translateX(24px)' : 'translateX(0)' }}></span>
                                </span>
                            </label>
                        </div>
                    </div>
                );
            case 'privacy':
                return (
                    <div>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: 'var(--text-main)', borderBottom: '1px solid rgba(255,255,255,0.4)', paddingBottom: '0.5rem' }}>🔒 Privacy & Security</h2>
                        <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.4)', borderRadius: '12px' }}>
                            <h4 style={{ margin: '0 0 1rem 0' }}>Password Management</h4>
                            <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>To change your password, verify your identity on the Profile page.</p>
                            <button onClick={() => navigate('/profile')} className="btn-secondary">Go to Profile</button>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto', display: 'grid', gridTemplateColumns: '250px 1fr', gap: '2rem' }}>
            <div className="glass-card" style={{ padding: '1rem', height: 'fit-content' }}>
                <button
                    onClick={() => setActiveTab('general')}
                    style={{ display: 'block', width: '100%', textAlign: 'left', padding: '1rem', background: activeTab === 'general' ? 'rgba(79, 70, 229, 0.1)' : 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', color: activeTab === 'general' ? 'var(--primary)' : 'var(--text-muted)', fontWeight: 600, marginBottom: '0.5rem', transition: 'all 0.2s' }}
                >
                    ⚙️ General
                </button>
                <button
                    onClick={() => setActiveTab('notifications')}
                    style={{ display: 'block', width: '100%', textAlign: 'left', padding: '1rem', background: activeTab === 'notifications' ? 'rgba(79, 70, 229, 0.1)' : 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', color: activeTab === 'notifications' ? 'var(--primary)' : 'var(--text-muted)', fontWeight: 600, marginBottom: '0.5rem', transition: 'all 0.2s' }}
                >
                    🔔 Notifications
                </button>
                <button
                    onClick={() => setActiveTab('privacy')}
                    style={{ display: 'block', width: '100%', textAlign: 'left', padding: '1rem', background: activeTab === 'privacy' ? 'rgba(79, 70, 229, 0.1)' : 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer', color: activeTab === 'privacy' ? 'var(--primary)' : 'var(--text-muted)', fontWeight: 600, transition: 'all 0.2s' }}
                >
                    🔒 Privacy
                </button>
            </div>
            <div className="glass-card" style={{ padding: '2.5rem', minHeight: '500px' }}>
                {renderContent()}
            </div>
        </div>
    );
}

export default Settings;
