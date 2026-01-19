import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/LandingPage.css'; // Ensure Landing Page styles are available

function RoleSelection() {
    const navigate = useNavigate();

    return (
        <div className="landing-container">
            {/* Same Navigation as Landing Page */}
            <nav className="landing-nav">
                <div className="nav-content">
                    <div className="nav-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
                        <span className="logo-icon">📚</span>
                        <span className="logo-text">Instant Library</span>
                    </div>
                    <div className="nav-links">
                        <Link to="/" className="nav-link">Home</Link>
                        <Link to="/about" className="nav-link">About</Link>
                        <Link to="/register" className="btn-primary small">Get Started</Link>
                    </div>
                </div>
            </nav>

            {/* Main Content Area - Centered like a Hero but for Selection */}
            <div className="page-center" style={{ minHeight: 'calc(100vh - 80px)', paddingTop: '80px' }}>
                <div style={{ width: '100%', maxWidth: '1000px', padding: '2rem' }}>
                    <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
                        <div className="hero-badge">Welcome Back</div>
                        <h1 className="hero-title" style={{ fontSize: '3rem', marginBottom: '1.5rem' }}>
                            Choose Your <span className="gradient-text">Portal</span>
                        </h1>
                        <p className="hero-subtitle" style={{ marginBottom: '0' }}>
                            Select your role to access the library dashboard.
                        </p>
                    </div>

                    <div className="features-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                        {/* Student Card */}
                        <div
                            className="glass-card role-card"
                            onClick={() => navigate('/student-login')}
                            style={{
                                cursor: 'pointer',
                                padding: '3rem 2rem',
                                textAlign: 'center',
                                transition: 'all 0.3s ease',
                                position: 'relative',
                                overflow: 'hidden'
                            }}
                        >
                            <div style={{
                                width: '80px', height: '80px', background: 'rgba(79, 70, 229, 0.1)',
                                borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontSize: '2.5rem', margin: '0 auto 1.5rem'
                            }}>
                                🎓
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-main)' }}>Student</h3>
                            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                                Access book catalog, request resources, and manage your study materials.
                            </p>
                            <button className="btn-primary" style={{ width: '100%' }}>Student Login</button>
                        </div>

                        {/* Staff Card */}
                        <div
                            className="glass-card role-card"
                            onClick={() => navigate('/staff-login')}
                            style={{
                                cursor: 'pointer',
                                padding: '3rem 2rem',
                                textAlign: 'center',
                                transition: 'all 0.3s ease',
                                position: 'relative',
                                overflow: 'hidden'
                            }}
                        >
                            <div style={{
                                width: '80px', height: '80px', background: 'rgba(16, 185, 129, 0.1)',
                                borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontSize: '2.5rem', margin: '0 auto 1.5rem'
                            }}>
                                👨‍💼
                            </div>
                            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text-main)' }}>Staff</h3>
                            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                                Manage inventory, process student requests, and track library assets.
                            </p>
                            <button className="btn-secondary" style={{ width: '100%', borderColor: 'var(--text-muted)' }}>Staff Login</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RoleSelection;
