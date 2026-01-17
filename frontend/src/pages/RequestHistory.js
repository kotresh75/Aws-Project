import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

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

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending':
                return '#f59e0b';
            case 'approved':
                return '#10b981';
            case 'rejected':
                return '#ef4444';
            case 'completed':
                return '#6366f1';
            default:
                return '#6b7280';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'pending':
                return '⏳';
            case 'approved':
                return '✅';
            case 'rejected':
                return '❌';
            case 'completed':
                return '📖';
            default:
                return '📝';
        }
    };

    const formatDate = (dateString) => {
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return dateString;
        }
    };

    return (
        <>
            <Breadcrumb pageTitle="History" />
            <div className="requests-container">
                <div className="requests-content">
                    <div className="requests-header">
                        <h1>📋 My Book Requests</h1>
                        <p>Track and manage all your book requests</p>
                    </div>

                    {message && (
                        <div className="message" style={{
                            padding: '12px 16px',
                            marginBottom: '20px',
                            borderRadius: '8px',
                            backgroundColor: '#fee2e2',
                            color: '#991b1b',
                            textAlign: 'center'
                        }}>
                            {message}
                        </div>
                    )}

                    <div className="requests-stats">
                        <div className="stat-card">
                            <span className="stat-number">{requests.filter(r => r.status === 'pending').length}</span>
                            <span className="stat-label">Pending</span>
                        </div>
                        <div className="stat-card">
                            <span className="stat-number">{requests.filter(r => r.status === 'approved').length}</span>
                            <span className="stat-label">Approved</span>
                        </div>
                        <div className="stat-card">
                            <span className="stat-number">{requests.filter(r => r.status === 'completed').length}</span>
                            <span className="stat-label">Completed</span>
                        </div>
                        <div className="stat-card">
                            <span className="stat-number">{requests.filter(r => r.status === 'rejected').length}</span>
                            <span className="stat-label">Rejected</span>
                        </div>
                    </div>

                    {requests.length > 0 ? (
                        <div className="requests-list">
                            {requests.map(request => (
                                <div key={request.request_id} className="request-card">
                                    <div className="request-header">
                                        <div>
                                            <h3>{request.book_name}</h3>
                                            <p className="request-author">by {request.author}</p>
                                        </div>
                                        <div className="status-badge" style={{
                                            backgroundColor: getStatusColor(request.status) + '20',
                                            borderLeft: `4px solid ${getStatusColor(request.status)}`
                                        }}>
                                            <span style={{ color: getStatusColor(request.status), fontWeight: '600' }}>
                                                {getStatusIcon(request.status)} {request.status.toUpperCase()}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="request-details">
                                        <div className="detail-row">
                                            <span className="detail-label">Request ID:</span>
                                            <span>#{request.request_id}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">Requested:</span>
                                            <span>{formatDate(request.requested_at)}</span>
                                        </div>
                                        <div className="detail-row">
                                            <span className="detail-label">Last Updated:</span>
                                            <span>{formatDate(request.updated_at)}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <h2>📚 No Requests Yet</h2>
                            <p>You haven't made any book requests yet.</p>
                            <a href="/catalog" className="cta-button">Browse Books →</a>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

export default RequestHistory;
