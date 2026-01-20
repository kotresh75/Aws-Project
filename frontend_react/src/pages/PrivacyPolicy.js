import React from 'react';
import { useNavigate } from 'react-router-dom';

function PrivacyPolicy() {
    const navigate = useNavigate();
    return (
        <div className="page-center">
            <div className="glass-card" style={{ maxWidth: '800px', width: '100%', padding: '3rem' }}>
                <button onClick={() => navigate(-1)} style={{ marginBottom: '2rem', background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>← Go Back</button>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text-main), var(--text-muted))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Privacy Policy</h1>
                <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', fontStyle: 'italic' }}>Last updated: {new Date().toLocaleDateString()}</p>

                <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '1rem' }} className="custom-scrollbar">
                    <section style={{ marginTop: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary-dark)' }}>1. Information We Collect</h2>
                        <p style={{ color: 'var(--text-main)' }}>We collect information you provide directly to us, such as when you create an account, request a book, or communicate with us. This may include your name, email address, student ID, and academic details.</p>
                    </section>
                    <section style={{ marginTop: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary-dark)' }}>2. How We Use Your Information</h2>
                        <p style={{ color: 'var(--text-main)' }}>We use the information we collect to provide, maintain, and improve our services, such as processing your book requests, sending you notifications via AWS SNS, and managing your account.</p>
                    </section>
                    <section style={{ marginTop: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary-dark)' }}>3. Data Security</h2>
                        <p style={{ color: 'var(--text-main)' }}>We implement reasonable security measures to protect your personal information. Our infrastructure is powered by AWS Cloud, ensuring industry-standard security protocols.</p>
                    </section>
                </div>
            </div>
        </div>
    );
}

export default PrivacyPolicy;
