import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Register() {
    const [step, setStep] = useState(1);
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [rollNo, setRollNo] = useState('');
    const [semester, setSemester] = useState('');
    const [year, setYear] = useState('');
    const [otp, setOtp] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (!name.trim() || !email.trim() || !password || !rollNo || !semester || !year) {
            setError('Please fill in all required fields.');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address.');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters.');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/register/student', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email.toLowerCase(), name, password, roll_no: rollNo, semester, year }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('✅ OTP sent to your email (Check Terminal)');
                setTimeout(() => { setStep(2); setSuccess(''); }, 2000);
            } else {
                setError(`❌ ${data.error || 'Registration failed'}`);
            }
        } catch (err) {
            setError('❌ Network error. Is the backend running?');
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
            const response = await fetch('http://localhost:5000/api/verify-registration-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email.toLowerCase(), otp }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess('✅ Registration successful! Redirecting...');
                setTimeout(() => { navigate('/login'); }, 2000);
            } else {
                setError(`❌ ${data.error || 'OTP verification failed'}`);
            }
        } catch (err) {
            setError('❌ Connection failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '600px', width: '100%', padding: '2.5rem' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Student Registration
                </h1>
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '2rem' }}>
                    Join the Instant Library today
                </p>

                {step === 1 ? (
                    <form onSubmit={handleRegister}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div className="form-group">
                                <label htmlFor="name">Full Name</label>
                                <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required disabled={loading} placeholder="John Doe" />
                            </div>
                            <div className="form-group">
                                <label htmlFor="email">Email</label>
                                <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={loading} placeholder="student@edu.com" />
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                            <div className="form-group">
                                <label htmlFor="rollNo">Roll No</label>
                                <input id="rollNo" type="text" value={rollNo} onChange={(e) => setRollNo(e.target.value)} required disabled={loading} />
                            </div>
                            <div className="form-group">
                                <label htmlFor="semester">Semester</label>
                                <input id="semester" type="text" value={semester} onChange={(e) => setSemester(e.target.value)} required disabled={loading} />
                            </div>
                            <div className="form-group">
                                <label htmlFor="year">Year</label>
                                <input id="year" type="text" value={year} onChange={(e) => setYear(e.target.value)} required disabled={loading} />
                            </div>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                            <div className="form-group">
                                <label htmlFor="password">Password</label>
                                <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={loading} />
                            </div>
                            <div className="form-group">
                                <label htmlFor="confirmPassword">Confirm</label>
                                <input id="confirmPassword" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required disabled={loading} />
                            </div>
                        </div>

                        {error && <div className="error-message">{error}</div>}
                        {success && <div className="success-message">{success}</div>}

                        <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '2rem', padding: '1rem' }}>
                            {loading ? 'Processing...' : 'Register'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOTP}>
                        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📧</div>
                            <h3 style={{ marginBottom: '0.5rem', color: 'var(--text-main)' }}>Verify Email</h3>
                            <p style={{ color: 'var(--text-muted)' }}>Enter the 6-digit OTP sent to <strong>{email}</strong></p>
                        </div>

                        <div className="form-group">
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

                        <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: '2rem', padding: '1rem' }}>
                            {loading ? 'Verifying...' : 'Verify OTP'}
                        </button>
                        <button type="button" onClick={() => setStep(1)} className="btn-secondary" style={{ width: '100%', marginTop: '1rem', border: 'none', background: 'transparent' }}>
                            Back to Registration
                        </button>
                    </form>
                )}

                <div style={{ marginTop: '2rem', textAlign: 'center', paddingTop: '1.5rem', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                    <p style={{ color: 'var(--text-muted)' }}>
                        Already have an account? <a href="/login" style={{ fontWeight: 600 }}>Login here</a>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Register;
