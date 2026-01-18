import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LandingPage.css'; // Global styles cover this now, but kept for legacy checks

function RoleSelection() {
    const navigate = useNavigate();

    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '900px', width: '100%', padding: '3rem', textAlign: 'center' }}>
                <div style={{ marginBottom: '3rem' }}>
                    <h1 style={{
                        fontSize: '3rem',
                        background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        marginBottom: '1rem'
                    }}>Welcome Back</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>Please select your role to login</p>
                </div>

                <div className="features-grid" style={{ gap: '2rem' }}>
                    {/* Student Card */}
                    <div
                        onClick={() => navigate('/student-login')}
                        style={{
                            cursor: 'pointer',
                            padding: '2rem',
                            background: 'rgba(255,255,255,0.4)',
                            border: '1px solid rgba(255,255,255,0.5)',
                            borderRadius: '16px',
                            transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-5px)';
                            e.currentTarget.style.background = 'rgba(255,255,255,0.8)';
                            e.currentTarget.style.boxShadow = '0 10px 25px rgba(37, 99, 235, 0.1)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'none';
                            e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        <div style={{ fontSize: '3rem', marginBottom: '1rem', background: '#dbeafe', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', margin: '0 auto 1rem' }}>🎓</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Student</h3>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Access book catalog, request books, and view your history.</p>
                        <button className="btn-primary" style={{ width: '100%' }}>Student Login</button>
                    </div>

                    {/* Staff Card */}
                    <div
                        onClick={() => navigate('/staff-login')}
                        style={{
                            cursor: 'pointer',
                            padding: '2rem',
                            background: 'rgba(255,255,255,0.4)',
                            border: '1px solid rgba(255,255,255,0.5)',
                            borderRadius: '16px',
                            transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-5px)';
                            e.currentTarget.style.background = 'rgba(255,255,255,0.8)';
                            e.currentTarget.style.boxShadow = '0 10px 25px rgba(217, 119, 6, 0.1)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'none';
                            e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    >
                        <div style={{ fontSize: '3rem', marginBottom: '1rem', background: '#fef3c7', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', margin: '0 auto 1rem' }}>👨‍💼</div>
                        <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Staff</h3>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Manage inventory, process requests, and track circulation.</p>
                        <button className="btn-primary" style={{ width: '100%', background: 'linear-gradient(135deg, var(--secondary), #b45309)' }}>Staff Login</button>
                    </div>
                </div>

                <div style={{ marginTop: '3rem' }}>
                    <button
                        onClick={() => navigate('/')}
                        style={{ background: 'none', border: 'none', color: 'var(--text-muted)', textDecoration: 'underline', cursor: 'pointer', fontSize: '1rem' }}
                    >
                        ← Back to Home
                    </button>
                </div>
            </div>
        </div>
    );
}

export default RoleSelection;
