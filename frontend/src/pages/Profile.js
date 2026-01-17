import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Breadcrumb from '../components/Breadcrumb';

function Profile() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        role: ''
    });
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (!userData) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(userData);
            setUser(parsedUser);
            setFormData({
                name: parsedUser.name,
                email: parsedUser.email,
                role: parsedUser.role
            });
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handlePasswordChange = (e) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSaveProfile = async (e) => {
        e.preventDefault();

        if (!formData.name.trim()) {
            setMessage('Name cannot be empty');
            return;
        }

        if (!formData.email.trim()) {
            setMessage('Email cannot be empty');
            return;
        }

        try {
            // Update localStorage with new user data
            const updatedUser = {
                ...user,
                name: formData.name,
                email: formData.email
            };
            localStorage.setItem('user', JSON.stringify(updatedUser));
            setUser(updatedUser);
            setIsEditing(false);
            setMessage('Profile updated successfully!');

            // Clear message after 3 seconds
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            setMessage('Error updating profile');
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();

        if (!passwordData.currentPassword) {
            setMessage('Please enter current password');
            return;
        }

        if (!passwordData.newPassword) {
            setMessage('Please enter new password');
            return;
        }

        if (passwordData.newPassword.length < 6) {
            setMessage('New password must be at least 6 characters');
            return;
        }

        if (passwordData.newPassword !== passwordData.confirmPassword) {
            setMessage('Passwords do not match');
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: user.email,
                    currentPassword: passwordData.currentPassword,
                    newPassword: passwordData.newPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                setMessage('Password changed successfully!');
                setPasswordData({
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: ''
                });
                setIsChangingPassword(false);
                setTimeout(() => setMessage(''), 3000);
            } else {
                setMessage(data.error || 'Error changing password');
            }
        } catch (error) {
            setMessage('Error changing password');
        }
    };

    if (!user) {
        return <div>Loading...</div>;
    }

    return (
        <>
            <Breadcrumb pageTitle="My Profile" />
            <div className="profile-container">
                <div className="profile-content">
                    <div className="profile-card">
                        <h1>My Profile</h1>

                        {message && (
                            <div className="message" style={{
                                padding: '12px 16px',
                                marginBottom: '20px',
                                borderRadius: '8px',
                                backgroundColor: message.includes('Error') ? '#fee2e2' : '#dcfce7',
                                color: message.includes('Error') ? '#991b1b' : '#15803d',
                                textAlign: 'center'
                            }}>
                                {message}
                            </div>
                        )}

                        {!isEditing && !isChangingPassword ? (
                            <div className="profile-info">
                                <div className="info-section">
                                    <label>Name</label>
                                    <p>{user.name}</p>
                                </div>
                                <div className="info-section">
                                    <label>Email</label>
                                    <p>{user.email}</p>
                                </div>
                                <div className="info-section">
                                    <label>Role</label>
                                    <p className="role-badge" style={{
                                        display: 'inline-block',
                                        padding: '6px 12px',
                                        borderRadius: '20px',
                                        backgroundColor: user.role === 'staff' ? '#dbeafe' : '#fce7f3',
                                        color: user.role === 'staff' ? '#0c4a6e' : '#831843',
                                        fontSize: '14px',
                                        fontWeight: '600',
                                        textTransform: 'uppercase'
                                    }}>
                                        {user.role}
                                    </p>
                                </div>
                                <div className="button-group">
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="edit-btn"
                                    >
                                        ✏️ Edit Profile
                                    </button>
                                    <button
                                        onClick={() => setIsChangingPassword(true)}
                                        className="change-password-btn"
                                    >
                                        🔐 Change Password
                                    </button>
                                </div>
                            </div>
                        ) : isChangingPassword ? (
                            <form onSubmit={handleChangePassword} className="profile-form">
                                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Change Password</h2>
                                <div className="form-group">
                                    <label>Current Password</label>
                                    <input
                                        type="password"
                                        name="currentPassword"
                                        value={passwordData.currentPassword}
                                        onChange={handlePasswordChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>New Password</label>
                                    <input
                                        type="password"
                                        name="newPassword"
                                        value={passwordData.newPassword}
                                        onChange={handlePasswordChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Confirm New Password</label>
                                    <input
                                        type="password"
                                        name="confirmPassword"
                                        value={passwordData.confirmPassword}
                                        onChange={handlePasswordChange}
                                        required
                                    />
                                </div>
                                <div className="form-actions">
                                    <button type="submit" className="save-btn">Change Password</button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setIsChangingPassword(false);
                                            setPasswordData({
                                                currentPassword: '',
                                                newPassword: '',
                                                confirmPassword: ''
                                            });
                                        }}
                                        className="cancel-btn"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <form onSubmit={handleSaveProfile} className="profile-form">
                                <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Edit Profile</h2>
                                <div className="form-group">
                                    <label>Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Role</label>
                                    <input
                                        type="text"
                                        value={formData.role}
                                        disabled
                                        style={{ opacity: 0.6, cursor: 'not-allowed' }}
                                    />
                                    <small style={{ color: '#6b7280', marginTop: '4px' }}>
                                        Role cannot be changed
                                    </small>
                                </div>
                                <div className="form-actions">
                                    <button type="submit" className="save-btn">Save Changes</button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setIsEditing(false);
                                            setFormData({
                                                name: user.name,
                                                email: user.email,
                                                role: user.role
                                            });
                                        }}
                                        className="cancel-btn"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export default Profile;
