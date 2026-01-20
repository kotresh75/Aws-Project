import React from 'react';
import { useNavigate } from 'react-router-dom';

function ServerError() {
    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '500px', width: '100%', padding: '3rem', textAlign: 'center', borderLeft: '4px solid var(--warning)' }}>
                <h1 style={{ fontSize: '5rem', color: 'var(--warning)', margin: 0, lineHeight: 1, filter: 'drop-shadow(0 4px 4px rgba(245, 158, 11, 0.2))' }}>500</h1>
                <h2 style={{ fontSize: '2rem', color: 'var(--warning)', marginTop: '0.5rem' }}>Server Error</h2>
                <p style={{ color: 'var(--text-main)', margin: '1rem 0 2rem' }}>
                    Oops! Something went wrong on our end. Please try again later or contact support.
                </p>
                <button
                    onClick={() => window.location.reload()}
                    className="btn-primary"
                    style={{ background: 'linear-gradient(135deg, var(--warning), #b45309)' }}
                >
                    Refresh Page
                </button>
            </div>
        </div>
    );
}

export default ServerError;
