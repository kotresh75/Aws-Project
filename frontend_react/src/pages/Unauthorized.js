import React from 'react';
import { useNavigate } from 'react-router-dom';

function Unauthorized() {
    const navigate = useNavigate();

    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '500px', width: '100%', padding: '3rem', textAlign: 'center', borderLeft: '4px solid var(--danger)' }}>
                <h1 style={{ fontSize: '5rem', color: 'var(--danger)', margin: 0, lineHeight: 1, filter: 'drop-shadow(0 4px 4px rgba(220, 38, 38, 0.2))' }}>403</h1>
                <h2 style={{ fontSize: '2rem', color: 'var(--danger)', marginTop: '0.5rem' }}>Access Denied</h2>
                <p style={{ color: 'var(--text-main)', margin: '1rem 0 2rem' }}>
                    You do not have permission to access this page. Please log in with an appropriate account.
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button
                        onClick={() => navigate(-1)}
                        className="btn-secondary"
                    >
                        Go Back
                    </button>
                    <button
                        onClick={() => navigate('/login')}
                        className="btn-primary"
                        style={{ background: 'linear-gradient(135deg, var(--danger), #b91c1c)' }}
                    >
                        Login
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Unauthorized;
