import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Profile() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({ name: '', email: '', role: '', roll_no: '', semester: '', year: '' });
    const [passwordData, setPasswordData] = useState({ currentPassword: '', newPassword: '', confirmPassword: '' });
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) { navigate('/login'); }
        else {
            const parsedUser = JSON.parse(userData);
            setUser(parsedUser);
            setFormData({
                name: parsedUser.name || '',
                email: parsedUser.email || '',
                role: parsedUser.role || '',
                roll_no: parsedUser.roll_no || '',
                semester: parsedUser.semester || '',
                year: parsedUser.year || ''
            });
        }
    }, [navigate]);

    const handleSaveProfile = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:5000/api/update-profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: user.email, name: formData.name, roll_no: formData.roll_no, semester: formData.semester, year: formData.year })
            });
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('user', JSON.stringify(data.user));
                setUser(data.user); setIsEditing(false); setMessage('✅ Profile updated successfully!');
                setTimeout(() => setMessage(''), 3000);
            } else { setMessage(data.error || 'Error updating profile'); }
        } catch (error) { setMessage('Error updating profile'); }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        if (passwordData.newPassword !== passwordData.confirmPassword) { setMessage('Passwords do not match'); return; }
        try {
            const response = await fetch('http://localhost:5000/api/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: user.email, currentPassword: passwordData.currentPassword, newPassword: passwordData.newPassword })
            });
            const data = await response.json();
            if (response.ok) {
                setMessage('✅ Password changed successfully!');
                setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
                setIsChangingPassword(false);
                setTimeout(() => setMessage(''), 3000);
            } else { setMessage(data.error || 'Error changing password'); }
        } catch (error) { setMessage('Error changing password'); }
    };

    if (!user) return <div>Loading...</div>;

    return (
        <div className="page-container">
            <div className="glass-card" style={{ maxWidth: '800px', width: '100%', margin: '0 auto', padding: '2.5rem' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '2rem', background: 'linear-gradient(135deg, var(--primary), var(--secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    My Profile
                </h1>

                {message && <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`} style={{ marginBottom: '1.5rem' }}>{message}</div>}

                {!isEditing && !isChangingPassword ? (
                    <div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                            <div>
                                <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Full Name</label>
                                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{user.name}</div>
                            </div>
                            <div>
                                <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Email</label>
                                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{user.email}</div>
                            </div>
                            {user.role === 'student' && (
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                                    <div><label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Roll No</label><div>{user.roll_no || '-'}</div></div>
                                    <div><label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Semester</label><div>{user.semester || '-'}</div></div>
                                    <div><label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Year</label><div>{user.year || '-'}</div></div>
                                </div>
                            )}
                            <div>
                                <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Role</label>
                                <div><span className="badge badge-primary">{user.role}</span></div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button onClick={() => setIsEditing(true)} className="btn-primary" style={{ flex: 1 }}>Edit Profile</button>
                            <button onClick={() => setIsChangingPassword(true)} className="btn-secondary" style={{ flex: 1 }}>Change Password</button>
                        </div>
                    </div>
                ) : isEditing ? (
                    <form onSubmit={handleSaveProfile}>
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Full Name</label>
                            <input type="text" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                        </div>
                        {user.role === 'student' && (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                <div><label>Roll No</label><input type="text" value={formData.roll_no} onChange={e => setFormData({ ...formData, roll_no: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '8px', border: '1px solid #ccc' }} /></div>
                                <div><label>Semester</label><input type="text" value={formData.semester} onChange={e => setFormData({ ...formData, semester: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '8px', border: '1px solid #ccc' }} /></div>
                                <div><label>Year</label><input type="text" value={formData.year} onChange={e => setFormData({ ...formData, year: e.target.value })} style={{ width: '100%', padding: '0.5rem', borderRadius: '8px', border: '1px solid #ccc' }} /></div>
                            </div>
                        )}
                        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                            <button type="submit" className="btn-primary" style={{ flex: 1 }}>Save Changes</button>
                            <button onClick={() => setIsEditing(false)} className="btn-secondary" style={{ flex: 1 }}>Cancel</button>
                        </div>
                    </form>
                ) : (
                    <form onSubmit={handleChangePassword}>
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Current Password</label>
                            <input type="password" value={passwordData.currentPassword} onChange={e => setPasswordData({ ...passwordData, currentPassword: e.target.value })} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                        </div>
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>New Password</label>
                            <input type="password" value={passwordData.newPassword} onChange={e => setPasswordData({ ...passwordData, newPassword: e.target.value })} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                        </div>
                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ display: 'block', marginBottom: '0.5rem' }}>Confirm Password</label>
                            <input type="password" value={passwordData.confirmPassword} onChange={e => setPasswordData({ ...passwordData, confirmPassword: e.target.value })} required style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ccc' }} />
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                            <button type="submit" className="btn-primary" style={{ flex: 1 }}>Update Password</button>
                            <button onClick={() => setIsChangingPassword(false)} className="btn-secondary" style={{ flex: 1 }}>Cancel</button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}

export default Profile;
