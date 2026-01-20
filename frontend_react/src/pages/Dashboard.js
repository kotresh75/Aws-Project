import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({
        totalBooks: 0,
        availableBooks: 0,
        totalStudents: 0,
        pendingRequests: 0,
        myActiveRequests: 0,
        myBorrowedBooks: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);
    const [loading, setLoading] = useState(true);

    const user = JSON.parse(localStorage.getItem('user') || 'null');

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        fetchDashboardData();
    }, [navigate]);

    const fetchDashboardData = async () => {
        try {
            const booksRes = await fetch('http://127.0.0.1:5000/api/books');
            const books = booksRes.ok ? await booksRes.json() : [];
            const totalBooks = books.length;
            const availableBooks = books.reduce((acc, book) => acc + book.available_count, 0);

            let newStats = { totalBooks, availableBooks };
            let activity = [];

            if (user.role === 'staff') {
                const studentsRes = await fetch('http://127.0.0.1:5000/api/users?role=student');
                const students = studentsRes.ok ? await studentsRes.json() : [];
                const requestsRes = await fetch(`http://127.0.0.1:5000/api/all-requests?staff_email=${user.email}`);
                const requests = requestsRes.ok ? await requestsRes.json() : [];

                newStats.totalStudents = students.length;
                newStats.pendingRequests = requests.filter(r => r.status === 'pending').length;
                activity = requests.slice(0, 5);
            } else {
                const requestsRes = await fetch(`http://127.0.0.1:5000/api/user-requests/${user.email}`);
                const requests = requestsRes.ok ? await requestsRes.json() : [];

                newStats.myActiveRequests = requests.filter(r => r.status === 'pending' || r.status === 'approved').length;
                newStats.myBorrowedBooks = requests.filter(r => r.status === 'approved').length;
                activity = requests.slice(0, 5);
            }

            setStats(prev => ({ ...prev, ...newStats }));
            setRecentActivity(activity);
        } catch (error) {
            console.error("Error fetching dashboard data", error);
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;
    if (loading) return <div className="loading">Loading dashboard...</div>;

    return (
        <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
            {/* Welcome Section */}
            <div className="glass-card" style={{ marginBottom: '2rem', background: 'rgba(255,255,255,0.6)' }}>
                <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Welcome back, {user.name}!
                </h1>
                <p style={{ color: 'var(--text-muted)' }}>Here's what's happening in your library today.</p>
            </div>

            {/* Stats Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <div className="glass-card">
                    <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Books</h3>
                    <p style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--primary)', margin: 0 }}>{stats.totalBooks}</p>
                </div>

                {user.role === 'staff' ? (
                    <>
                        <div className="glass-card">
                            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Students</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--success)', margin: 0 }}>{stats.totalStudents}</p>
                        </div>
                        <div className="glass-card">
                            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pending Requests</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--warning)', margin: 0 }}>{stats.pendingRequests}</p>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="glass-card">
                            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Books Available</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--success)', margin: 0 }}>{stats.availableBooks}</p>
                        </div>
                        <div className="glass-card">
                            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Active Requests</h3>
                            <p style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--warning)', margin: 0 }}>{stats.myActiveRequests}</p>
                        </div>
                    </>
                )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
                {/* Recent Activity */}
                <div className="glass-card">
                    <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', borderBottom: '1px solid rgba(0,0,0,0.1)', paddingBottom: '1rem' }}>Recent Activity</h2>
                    {recentActivity.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {recentActivity.map((item, idx) => (
                                <div key={idx} style={{ padding: '1rem', background: 'rgba(255,255,255,0.4)', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <p style={{ margin: '0 0 0.25rem 0', fontWeight: '600', color: 'var(--text-main)' }}>{item.book_name}</p>
                                        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>{user.role === 'staff' ? `Requested by ${item.sender}` : `Author: ${item.author}`}</p>
                                    </div>
                                    <span className={`badge ${item.status === 'approved' ? 'badge-success' : item.status === 'rejected' ? 'badge-danger' : 'badge-warning'}`}>
                                        {item.status}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No recent activity.</p>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="glass-card">
                    <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', borderBottom: '1px solid rgba(0,0,0,0.1)', paddingBottom: '1rem' }}>Quick Actions</h2>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {user.role === 'staff' ? (
                            <>
                                <button onClick={() => navigate('/book-management')} className="btn-secondary" style={{ textAlign: 'left', justifyContent: 'flex-start', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    <span style={{ fontSize: '1.5rem' }}>📚</span>
                                    <div>
                                        <div style={{ fontWeight: '600' }}>Manage Books</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Add, edit, or remove books</div>
                                    </div>
                                </button>
                                <button onClick={() => navigate('/request-management')} className="btn-secondary" style={{ textAlign: 'left', justifyContent: 'flex-start', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    <span style={{ fontSize: '1.5rem' }}>📋</span>
                                    <div>
                                        <div style={{ fontWeight: '600' }}>Manage Requests</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Approve or reject requests</div>
                                    </div>
                                </button>
                                <button onClick={() => navigate('/student-management')} className="btn-secondary" style={{ textAlign: 'left', justifyContent: 'flex-start', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    <span style={{ fontSize: '1.5rem' }}>🎓</span>
                                    <div>
                                        <div style={{ fontWeight: '600' }}>Manage Students</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>View student history</div>
                                    </div>
                                </button>
                            </>
                        ) : (
                            <>
                                <button onClick={() => navigate('/catalog')} className="btn-secondary" style={{ textAlign: 'left', justifyContent: 'flex-start', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    <span style={{ fontSize: '1.5rem' }}>📖</span>
                                    <div>
                                        <div style={{ fontWeight: '600' }}>Browse Catalog</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Search and borrow books</div>
                                    </div>
                                </button>
                                <button onClick={() => navigate('/requests')} className="btn-secondary" style={{ textAlign: 'left', justifyContent: 'flex-start', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                    <span style={{ fontSize: '1.5rem' }}>📋</span>
                                    <div>
                                        <div style={{ fontWeight: '600' }}>My Requests</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Check status of your books</div>
                                    </div>
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
