import React from 'react';
import { useNavigate } from 'react-router-dom';

function ContactSupport() {
    const navigate = useNavigate();
    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '600px', width: '100%', padding: '3rem', textAlign: 'center' }}>
                <button onClick={() => navigate(-1)} style={{ marginBottom: '2rem', background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>← Go Back</button>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text-main), var(--text-muted))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Contact Support</h1>

                <div style={{ background: 'rgba(255,255,255,0.4)', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.5)', padding: '2rem', marginTop: '2rem' }}>
                    <span style={{ fontSize: '4rem', display: 'block', marginBottom: '1rem', filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.1))' }}>🎧</span>
                    <p style={{ fontSize: '1.25rem', marginBottom: '2rem', color: 'var(--text-main)' }}>
                        Need help with your account or finding a book?<br />Our support team is here for you.
                    </p>

                    <div style={{ display: 'inline-flex', gap: '1rem', flexDirection: 'column' }}>
                        <a href="mailto:support@instantlibrary.com" className="btn-primary" style={{ display: 'inline-block', padding: '1rem 2rem', textDecoration: 'none' }}>
                            Email Support
                        </a>
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Typical response time: 24 hours</p>
                    </div>

                    <div style={{ marginTop: '3rem', borderTop: '1px solid rgba(0,0,0,0.1)', paddingTop: '2rem' }}>
                        <h3 style={{ marginBottom: '0.5rem', color: 'var(--text-main)' }}>Visit Us</h3>
                        <p style={{ color: 'var(--text-muted)' }}>Central Library, Main Campus<br />University of Technology</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ContactSupport;
