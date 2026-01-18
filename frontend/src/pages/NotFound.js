import React from 'react';
import { useNavigate } from 'react-router-dom';

function NotFound() {
    const navigate = useNavigate();

    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '500px', width: '100%', padding: '3rem', textAlign: 'center' }}>
                <h1 style={{ fontSize: '6rem', background: 'linear-gradient(135deg, var(--text-main), var(--text-muted))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0, lineHeight: 1 }}>404</h1>
                <h2 style={{ fontSize: '2rem', color: 'var(--text-main)', marginTop: '0.5rem' }}>Page Not Found</h2>
                <p style={{ color: 'var(--text-muted)', margin: '1rem 0 2rem' }}>
                    The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
                </p>
                <button
                    onClick={() => navigate('/')}
                    className="btn-primary"
                >
                    Back to Home
                </button>
            </div>
        </div>
    );
}

export default NotFound;
