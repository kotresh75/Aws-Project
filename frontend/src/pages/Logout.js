import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        // Clear session data
        localStorage.removeItem('user');

        // Redirect to login/role selection
        setTimeout(() => {
            navigate('/login');
        }, 1500); // Slight delay to show the "Logging out" animation
    }, [navigate]);

    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '400px', width: '100%', padding: '3rem', textAlign: 'center' }}>
                <h2 style={{ color: 'var(--text-main)', marginBottom: '1.5rem' }}>Logging out...</h2>
                <div className="spinner" style={{
                    width: '50px',
                    height: '50px',
                    border: '4px solid rgba(99, 102, 241, 0.1)',
                    borderTop: '4px solid var(--primary)',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    margin: '0 auto'
                }}></div>
                <style>
                    {`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}
                </style>
            </div>
        </div>
    );
}

export default Logout;
