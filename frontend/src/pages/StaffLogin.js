import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function StaffLogin() {
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
                if (data.role !== 'staff') {
                    setError('Access Restricted: Please use the Student Login page.');
                    return;
                }
                localStorage.setItem('user', JSON.stringify({
                    email: data.email,
                    name: data.name,
                    role: data.role,
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
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '420px', width: '100%' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h1 style={{
                        fontSize: '2rem',
                        background: 'linear-gradient(135deg, var(--secondary), #b45309)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        marginBottom: '0.5rem'
                    }}>Staff Login</h1>
                    <p style={{ color: 'var(--text-muted)' }}>Administrative Access</p>
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
                            placeholder="staff@university.edu"
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

                    <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '1rem', padding: '1rem', background: 'linear-gradient(135deg, var(--secondary), #b45309)' }}>
                        {loading ? 'Logging in...' : 'Sign In'}
                    </button>

                    <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                        <button
                            type="button"
                            onClick={() => navigate('/login')}
                            style={{ background: 'none', color: 'var(--text-muted)', textDecoration: 'underline' }}
                        >
                            ← Back to Role Selection
                        </button>
                    </div>
                </form>

                <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(0,0,0,0.1)', textAlign: 'center' }}>
                    <p>
                        <a href="/forgot-password" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Forgot password?</a>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default StaffLogin;
