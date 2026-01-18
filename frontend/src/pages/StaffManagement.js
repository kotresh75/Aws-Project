import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function StaffManagement() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData || JSON.parse(userData).role !== 'staff') { navigate('/login'); }
    }, [navigate]);

    const handleAddStaff = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) { setMessage('Error: Passwords do not match'); return; }
        if (password.length < 6) { setMessage('Error: Password must be 6+ chars'); return; }
        setLoading(true);

        try {
            const userData = JSON.parse(localStorage.getItem('user'));
            const response = await fetch('http://localhost:5000/api/admin/register-staff', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ caller_email: userData.email, email: email.toLowerCase(), name, password }),
            });
            const data = await response.json();
            if (response.ok) {
                setMessage(`✅ Staff account created for ${email}`);
                setName(''); setEmail(''); setPassword(''); setConfirmPassword('');
            } else { setMessage(`Error: ${data.error}`); }
        } catch (err) { setMessage('Error: Network failed'); } finally { setLoading(false); }
    };

    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '500px', width: '100%', padding: '2.5rem' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '0.5rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Add Staff Member
                </h1>
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '2rem' }}>Create a new administrator account</p>

                {message && <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`} style={{ marginBottom: '1.5rem' }}>{message}</div>}

                <form onSubmit={handleAddStaff}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Full Name</label>
                        <input type="text" value={name} onChange={e => setName(e.target.value)} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email</label>
                        <input type="email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Password</label>
                        <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Confirm Password</label>
                        <input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                    </div>
                    <button type="submit" className="btn-primary" style={{ width: '100%' }} disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</button>
                </form>
            </div>
        </div>
    );
}

export default StaffManagement;
