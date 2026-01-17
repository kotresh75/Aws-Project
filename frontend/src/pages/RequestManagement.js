import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function RequestManagement() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [requests, setRequests] = useState([]);
    const [message, setMessage] = useState('');
    const [filter, setFilter] = useState('pending');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(userData);
            if (parsedUser.role !== 'staff') {
                navigate('/dashboard');
            } else {
                setUser(parsedUser);
                fetchAllRequests(parsedUser.email);
            }
        }
    }, [navigate]);

    const fetchAllRequests = async (staffEmail) => {
        try {
            const response = await fetch(`http://localhost:5000/api/all-requests?staff_email=${staffEmail}`);
            const data = await response.json();
            setRequests(data);
        } catch (error) {
            setMessage('Error fetching requests');
        }
    };

    const handleUpdateStatus = async (requestId, newStatus) => {
        try {
            const response = await fetch(`http://localhost:5000/api/requests/${requestId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: newStatus
                })
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(`✅ Request updated to ${newStatus}`);
                fetchAllRequests(user.email);
                setTimeout(() => setMessage(''), 3000);
            } else {
                setMessage(data.error || 'Error updating request');
            }
        } catch (error) {
            setMessage('Error updating request');
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

    const filteredRequests = filter === 'all' ? requests : requests.filter(r => r.status === filter);

    return (
        <>
            <Breadcrumb pageTitle="Manage Requests" />
            <div className="request-management-container">
                <div className="request-management-content">
                    <div className="management-header">
                        <h1>📋 Request Management</h1>
                        <p>Review and manage student book requests</p>
                    </div>
                    {message && (
                        <div className="message" style={{
                            padding: '12px 16px',
                            marginBottom: '20px',
                            borderRadius: '8px',
                            backgroundColor: message.includes('Error') ? '#fee2e2' : '#dcfce7',
                            color: message.includes('Error') ? '#991b1b' : '#15803d',
                            textAlign: 'center'
                        }}>
                            {message}
                        </div>
                    )}

                    <div className="filter-tabs">
                        {['all', 'pending', 'approved', 'rejected', 'completed'].map(status => (
                            <button
                                key={status}
                                onClick={() => setFilter(status)}
                                className={`filter-tab ${filter === status ? 'active' : ''}`}
                                style={filter === status ? {
                                    borderBottomColor: getStatusColor(status === 'all' ? 'pending' : status),
                                    color: getStatusColor(status === 'all' ? 'pending' : status)
                                } : {}}
                            >
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                                <span className="count">({filteredRequests.length})</span>
                            </button>
                        ))}
                    </div>

                    <div className="requests-management-list">
                        {filteredRequests.length > 0 ? (
                            filteredRequests.map(request => (
                                <div key={request.request_id} className="management-request-card">
                                    <div className="request-info">
                                        <div className="request-book">
                                            <h3>{request.book_name}</h3>
                                            <p className="request-author">by {request.author}</p>
                                        </div>
                                        <div className="request-user">
                                            <p><strong>Student:</strong> {request.email}</p>
                                            <p><strong>Requested:</strong> {formatDate(request.requested_at)}</p>
                                        </div>
                                        <div className="current-status">
                                            <span style={{
                                                color: getStatusColor(request.status),
                                                fontWeight: '600'
                                            }}>
                                                Current: {request.status.toUpperCase()}
                                            </span>
                                        </div>
                                    </div>

                                    {request.status === 'pending' && (
                                        <div className="request-actions">
                                            <button
                                                onClick={() => handleUpdateStatus(request.request_id, 'approved')}
                                                className="approve-btn"
                                            >
                                                ✓ Approve
                                            </button>
                                            <button
                                                onClick={() => handleUpdateStatus(request.request_id, 'rejected')}
                                                className="reject-btn"
                                            >
                                                ✕ Reject
                                            </button>
                                        </div>
                                    )}

                                    {request.status === 'approved' && (
                                        <div className="request-actions">
                                            <button
                                                onClick={() => handleUpdateStatus(request.request_id, 'completed')}
                                                className="complete-btn"
                                            >
                                                ✓ Mark Complete
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))
                        ) : (
                            <div style={{ textAlign: 'center', padding: '2rem' }}>
                                <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>No requests with status "{filter}"</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export default RequestManagement;
