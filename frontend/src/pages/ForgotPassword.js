import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/LandingPage.css';

function ForgotPassword() {
    const [step, setStep] = useState(1); // step 1: email, step 2: verify OTP, step 3: reset password
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email.toLowerCase() }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('OTP sent to your terminal. Proceeding to verification...');
                setTimeout(() => {
                    setStep(2);
                    setSuccess('');
                }, 1500);
            } else {
                setError(data.error || 'Failed to send OTP');
            }
        } catch (err) {
            setError('Failed to connect to server. Is the backend running?');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/verify-forgot-password-otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email.toLowerCase(),
                    otp
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('OTP verified! Now set your new password.');
                setTimeout(() => {
                    setStep(3);
                    setSuccess('');
                }, 1500);
            } else {
                setError(data.error || 'OTP verification failed');
            }
        } catch (err) {
            setError('Failed to connect to server. Is the backend running?');
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordReset = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        if (newPassword !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        if (newPassword.length < 6) {
            setError('Password must be at least 6 characters');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email.toLowerCase(),
                    new_password: newPassword
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('Password reset successful! Redirecting to login...');
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                setError(data.error || 'Password reset failed');
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
                        <Link to="/login" className="nav-link">Login</Link>
                    </div>
                </div>
            </nav>

            <div className="auth-wrapper">
                <div className="glass-card" style={{ maxWidth: '420px', width: '100%', padding: '2.5rem' }}>
                    <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                        <h1 className="hero-title" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
                            Reset <span className="gradient-text">Password</span>
                        </h1>
                        <p style={{ color: 'var(--text-muted)' }}>Securely recover your account</p>
                    </div>

                    {step === 1 && (
                        <form onSubmit={handleEmailSubmit}>
                            <div className="form-group">
                                <label htmlFor="email">Enter your email address</label>
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    disabled={loading}
                                    placeholder="your@email.com"
                                />
                            </div>
                            {error && <div className="error-message">{error}</div>}
                            {success && <div className="success-message">{success}</div>}
                            <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                                {loading ? 'Sending OTP...' : 'Send OTP'}
                            </button>
                        </form>
                    )}

                    {step === 2 && (
                        <form onSubmit={handleVerifyOTP}>
                            <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                                OTP has been sent to your email/terminal.
                            </p>
                            <div className="form-group">
                                <label htmlFor="otp">Enter OTP (6 digits)</label>
                                <input
                                    id="otp"
                                    type="text"
                                    value={otp}
                                    onChange={(e) => setOtp(e.target.value)}
                                    placeholder="0 0 0 0 0 0"
                                    maxLength="6"
                                    required
                                    disabled={loading}
                                    style={{ textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5rem' }}
                                />
                            </div>
                            {error && <div className="error-message">{error}</div>}
                            {success && <div className="success-message">{success}</div>}
                            <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                                {loading ? 'Verifying...' : 'Verify OTP'}
                            </button>
                        </form>
                    )}

                    {step === 3 && (
                        <form onSubmit={handlePasswordReset}>
                            <div className="form-group">
                                <label htmlFor="newPassword">New Password</label>
                                <input
                                    id="newPassword"
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    required
                                    disabled={loading}
                                    placeholder="••••••••"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="confirmPassword">Confirm Password</label>
                                <input
                                    id="confirmPassword"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                    disabled={loading}
                                    placeholder="••••••••"
                                />
                            </div>
                            {error && <div className="error-message">{error}</div>}
                            {success && <div className="success-message">{success}</div>}
                            <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                                {loading ? 'Resetting...' : 'Reset Password'}
                            </button>
                        </form>
                    )}

                    <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(0,0,0,0.1)', textAlign: 'center' }}>
                        <p><Link to="/login" style={{ color: 'var(--text-muted)' }}>← Back to Login</Link></p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ForgotPassword;
