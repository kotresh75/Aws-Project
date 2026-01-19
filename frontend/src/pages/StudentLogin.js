import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/LandingPage.css';

function StudentLogin() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email.toLowerCase(), password }),
            });

            const data = await response.json();

            if (response.ok) {
                if (data.role !== 'student') {
                    setError('Access Restricted: Please use the Staff Login page.');
                    return;
                }
                localStorage.setItem('user', JSON.stringify({
                    email: data.email,
                    name: data.name,
                    role: data.role,
                    roll_no: data.roll_no,
                    semester: data.semester,
                    year: data.year
                }));
                navigate('/dashboard');
            } else {
                setError(data.error || 'Login failed');
            }
        } catch (err) {
            setError('Failed to connect to server. Is the backend running?');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="landing-container">
            {/* Standard Navigation */}
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

            <div className="auth-wrapper">
                <div className="glass-card" style={{ maxWidth: '420px', width: '100%' }}>
                    <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                        <h1 className="hero-title" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                            Student <span className="gradient-text">Login</span>
                        </h1>
                        <p style={{ color: 'var(--text-muted)' }}>Welcome back to Instant Library</p>
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="email">Email Address</label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                disabled={loading}
                                placeholder="Enter your email"
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                disabled={loading}
                                placeholder="••••••••"
                            />
                        </div>

                        {error && <div className="error-message">{error}</div>}

                        <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '1rem', padding: '1rem' }}>
                            {loading ? 'Logging in...' : 'Sign In'}
                        </button>

                        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                            <Link to="/login" style={{ color: 'var(--text-muted)', textDecoration: 'underline' }}>
                                ← Back to Role Selection
                            </Link>
                        </div>
                    </form>

                    <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(0,0,0,0.1)', textAlign: 'center' }}>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            Don't have an account? <Link to="/register" style={{ fontWeight: 600, color: 'var(--primary)' }}>Register here</Link>
                        </p>
                        <p style={{ marginTop: '0.5rem' }}>
                            <Link to="/forgot-password" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Forgot password?</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default StudentLogin;
