import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Notifications() {
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(userData);
            fetchNotifications(parsedUser.email);
        }
    }, [navigate]);

    const fetchNotifications = async (email) => {
        try {
            const response = await fetch(`http://localhost:5000/api/notifications?email=${email}`);
            if (response.ok) {
                const data = await response.json();
                data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                setNotifications(data);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleMarkAsRead = async (id) => {
        try {
            const response = await fetch(`http://localhost:5000/api/notifications/${id}/read`, { method: 'PUT' });
            if (response.ok) {
                setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
            }
        } catch (error) { }
    };

    const formatTimeAgo = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        if (seconds < 60) return 'Just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        return date.toLocaleDateString();
    };

    const getIconForMessage = (msg) => {
        const lower = msg.toLowerCase();
        if (lower.includes('approved')) return '✅';
        if (lower.includes('rejected')) return '❌';
        if (lower.includes('pending')) return '⏳';
        return '';
    };

    const unreadCount = notifications.filter(n => !n.read).length;

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <div className="glass-card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ fontSize: '1.8rem', margin: 0, color: 'var(--text-main)' }}>Notifications</h1>
                    <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                        You have {unreadCount} unread message{unreadCount !== 1 ? 's' : ''}
                    </p>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading...</div>
            ) : notifications.length === 0 ? (
                <div className="glass-card" style={{ textAlign: 'center', padding: '4rem' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
                    <h3 style={{ color: 'var(--text-main)', marginBottom: '0.5rem' }}>All caught up!</h3>
                    <p style={{ color: 'var(--text-muted)' }}>You have no new notifications.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {notifications.map(notif => (
                        <div
                            key={notif.id}
                            className={`glass-card ${!notif.read ? 'unread' : ''}`}
                            style={{
                                padding: '1.5rem',
                                background: notif.read ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.85)',
                                borderLeft: notif.read ? '1px solid rgba(255,255,255,0.4)' : '4px solid var(--primary)',
                                display: 'flex',
                                gap: '1.5rem',
                                transition: 'all 0.2s ease',
                                opacity: notif.read ? 0.8 : 1
                            }}
                            onMouseEnter={(e) => {
                                if (notif.read) e.currentTarget.style.opacity = 1;
                            }}
                            onMouseLeave={(e) => {
                                if (notif.read) e.currentTarget.style.opacity = 0.8;
                            }}
                        >
                            <div style={{
                                width: '40px', height: '40px', borderRadius: '50%',
                                background: notif.read ? 'rgba(0,0,0,0.05)' : 'rgba(79, 70, 229, 0.1)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0
                            }}>
                                {getIconForMessage(notif.message)}
                            </div>

                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>
                                        {notif.subject || 'Notification'}
                                    </h3>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                        {formatTimeAgo(notif.timestamp)}
                                    </span>
                                </div>
                                <p style={{ margin: 0, color: 'var(--text-main)', lineHeight: 1.5, fontSize: '0.95rem' }}>
                                    {notif.message}
                                </p>

                                {!notif.read && (
                                    <button
                                        onClick={(e) => { e.stopPropagation(); handleMarkAsRead(notif.id); }}
                                        style={{ marginTop: '0.5rem', color: 'var(--primary)', background: 'transparent', fontWeight: 600, fontSize: '0.85rem' }}
                                    >
                                        Mark as read
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default Notifications;
