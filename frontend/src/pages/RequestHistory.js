import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function RequestHistory() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [requests, setRequests] = useState([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(userData);
            setUser(parsedUser);
            fetchUserRequests(parsedUser.email);
        }
    }, [navigate]);

    const fetchUserRequests = async (email) => {
        try {
            const response = await fetch(`http://localhost:5000/api/user-requests/${email}`);
            const data = await response.json();
            setRequests(data);
        } catch (error) {
            setMessage('Error fetching requests');
        }
    };

    const formatDate = (dateString) => {
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        } catch (e) { return dateString; }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
            <div className="glass-card" style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    📋 Request History
                </h1>
                <p style={{ color: 'var(--text-muted)' }}>Track and manage all your book requests</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                {['pending', 'approved', 'completed', 'rejected'].map(status => {
                    const count = requests.filter(r => r.status === status).length;
                    let color = 'var(--primary)';
                    if (status === 'approved') color = 'var(--success)';
                    if (status === 'rejected') color = 'var(--danger)';
                    if (status === 'pending') color = 'var(--warning)';

                    return (
                        <div key={status} className="glass-card" style={{ textAlign: 'center', padding: '1rem' }}>
                            <div style={{ fontSize: '2rem', fontWeight: '800', color: color }}>{count}</div>
                            <div style={{ textTransform: 'uppercase', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '600' }}>{status}</div>
                        </div>
                    );
                })}
            </div>

            {requests.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {requests.map(request => (
                        <div key={request.request_id} className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem', borderLeft: `4px solid ${request.status === 'approved' ? 'var(--success)' : request.status === 'rejected' ? 'var(--danger)' : 'var(--warning)'}` }}>
                            <div>
                                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem', color: 'var(--text-main)' }}>{request.book_name}</h3>
                                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>by {request.author} • Request ID: #{request.request_id}</p>
                                <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Requested: {formatDate(request.requested_at)}</p>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <span className={`badge ${request.status === 'approved' ? 'badge-success' : request.status === 'rejected' ? 'badge-danger' : 'badge-warning'}`} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
                                    {request.status.toUpperCase()}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>You haven't made any book requests yet.</p>
                    <button onClick={() => navigate('/catalog')} className="btn-primary" style={{ marginTop: '1rem' }}>Browse Books</button>
                </div>
            )}
        </div>
    );
}

export default RequestHistory;
