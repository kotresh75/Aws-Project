import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function StaffManagement() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
            return;
        }

        const user = JSON.parse(userData);
        // Redirect non-staff users
        if (user.role !== 'staff') {
            navigate('/dashboard');
        }
    }, [navigate]);

    const handleAddStaff = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        // Validation
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            setLoading(false);
            return;
        }

        try {
            const userData = JSON.parse(localStorage.getItem('user'));

            const response = await fetch('http://localhost:5000/api/admin/register-staff', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    caller_email: userData.email,
                    email: email.toLowerCase(),
                    name,
                    password,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(`Staff account created successfully: ${email}`);
                setName('');
                setEmail('');
                setPassword('');
                setConfirmPassword('');
            } else {
                setError(data.error || 'Failed to create staff account');
            }
        } catch (err) {
            setError('Failed to connect to server. Is the backend running?');
        } finally {
            setLoading(false);
        }
    };

    const userData = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;

    if (!userData || userData.role !== 'staff') {
        return <div className="loading">Loading...</div>;
    }

    return (
        <>
            <Breadcrumb pageTitle="Staff" />
            <div className="staff-management-container">
                <div className="staff-management-content">
                    <div className="staff-management-box">
                        <h1>Add New Staff Member</h1>
                        <p className="subtitle">Create a new staff account</p>

                        <form onSubmit={handleAddStaff}>
                            <div className="form-group">
                                <label htmlFor="name">Full Name</label>
                                <input
                                    id="name"
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="email">Email</label>
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    disabled={loading}
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
                                />
                            </div>

                            {error && <div className="error-message">{error}</div>}
                            {success && <div className="success-message">{success}</div>}

                            <button type="submit" disabled={loading}>
                                {loading ? 'Creating Account...' : 'Add Staff Member'}
                            </button>
                        </form>

                        <div className="info-box">
                            <h3>Note</h3>
                            <p>New staff accounts are created immediately and do not require OTP verification.</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default StaffManagement;
