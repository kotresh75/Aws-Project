import React from 'react';
import { useNavigate } from 'react-router-dom';

function TermsOfService() {
    const navigate = useNavigate();
    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '800px', width: '100%', padding: '3rem' }}>
                <button onClick={() => navigate(-1)} style={{ marginBottom: '2rem', background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>← Go Back</button>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text-main), var(--text-muted))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Terms of Service</h1>

                <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '1rem' }} className="custom-scrollbar">
                    <section style={{ marginTop: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary-dark)' }}>1. Acceptance of Terms</h2>
                        <p style={{ color: 'var(--text-main)' }}>By accessing or using the Instant Library System, you agree to be bound by these Terms of Service. If you do not agree to these terms, you may not access or use our services.</p>
                    </section>
                    <section style={{ marginTop: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary-dark)' }}>2. User Responsibilities</h2>
                        <p style={{ color: 'var(--text-main)' }}>You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You agree to return borrowed books on time and in good condition.</p>
                    </section>
                    <section style={{ marginTop: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary-dark)' }}>3. Service Availability</h2>
                        <p style={{ color: 'var(--text-main)' }}>We strive to keep the service available 24/7, but we count on AWS guarantees. We are not liable for any downtime caused by maintenance or unforeseen technical issues.</p>
                    </section>
                </div>
            </div>
        </div>
    );
}

export default TermsOfService;
