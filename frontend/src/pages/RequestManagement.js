import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function RequestManagement() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [requests, setRequests] = useState([]);
    const [message, setMessage] = useState('');
    const [filter, setFilter] = useState('pending');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData || JSON.parse(userData).role !== 'staff') { navigate('/login'); }
        else { setUser(JSON.parse(userData)); fetchAllRequests(JSON.parse(userData).email); }
    }, [navigate]);

    const fetchAllRequests = async (staffEmail) => {
        try {
            const response = await fetch(`http://localhost:5000/api/all-requests?staff_email=${staffEmail}`);
            const data = await response.json();
            setRequests(data);
        } catch (error) { setMessage('Error fetching requests'); }
    };

    const handleUpdateStatus = async (requestId, newStatus) => {
        try {
            const response = await fetch(`http://localhost:5000/api/requests/${requestId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            if (response.ok) {
                setMessage(`✅ Request updated to ${newStatus}`);
                fetchAllRequests(user.email);
                setTimeout(() => setMessage(''), 3000);
            } else {
                const data = await response.json();
                setMessage(data.error || 'Error updating request');
            }
        } catch (error) { setMessage('Error updating request'); }
    };

    const formatDate = (dateString) => {
        try { return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); }
        catch (e) { return dateString; }
    };

    const filteredRequests = filter === 'all' ? requests : requests.filter(r => r.status === filter);

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            <div className="glass-card" style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    📋 Request Management
                </h1>
                <p style={{ color: 'var(--text-muted)' }}>Review and manage student book requests</p>

                {message && <div style={{ color: message.includes('Error') ? 'red' : 'green', margin: '1rem 0', fontWeight: 'bold' }}>{message}</div>}

                <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap', marginTop: '1.5rem' }}>
                    {['all', 'pending', 'approved', 'rejected', 'completed'].map(status => (
                        <button
                            key={status}
                            onClick={() => setFilter(status)}
                            className={filter === status ? 'btn-primary' : 'btn-secondary'}
                            style={{ textTransform: 'capitalize' }}
                        >
                            {status} ({status === 'all' ? requests.length : requests.filter(r => r.status === status).length})
                        </button>
                    ))}
                </div>
            </div>

            <div className="glass-table-container">
                <table className="glass-table">
                    <thead>
                        <tr>
                            <th>Book</th>
                            <th>Student</th>
                            <th>Requested At</th>
                            <th>Status Detail</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredRequests.map(request => (
                            <tr key={request.request_id}>
                                <td>
                                    <div style={{ fontWeight: 600 }}>{request.book_name}</div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>by {request.author}</div>
                                </td>
                                <td>{request.email}</td>
                                <td>{formatDate(request.requested_at)}</td>
                                <td>
                                    <span className={`badge ${request.status === 'approved' ? 'badge-success' : request.status === 'rejected' ? 'badge-danger' : 'badge-warning'}`}>
                                        {request.status.toUpperCase()}
                                    </span>
                                </td>
                                <td>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        {request.status === 'pending' && (
                                            <>
                                                <button onClick={() => handleUpdateStatus(request.request_id, 'approved')} className="btn-primary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>✓ Approve</button>
                                                <button onClick={() => handleUpdateStatus(request.request_id, 'rejected')} className="btn-danger" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>✕ Reject</button>
                                            </>
                                        )}
                                        {request.status === 'approved' && (
                                            <button onClick={() => handleUpdateStatus(request.request_id, 'completed')} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>✓ Complete</button>
                                        )}
                                        {(request.status === 'completed' || request.status === 'rejected') && (
                                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No actions</span>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {filteredRequests.length === 0 && (
                <div className="glass-card" style={{ textAlign: 'center', marginTop: '1rem', padding: '2rem', color: 'var(--text-muted)' }}>
                    No requests found matching this filter.
                </div>
            )}
        </div>
    );
}

export default RequestManagement;
