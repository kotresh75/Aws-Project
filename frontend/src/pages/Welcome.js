import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/LandingPage.css';

function Welcome() {
    const navigate = useNavigate();

    return (
        <div className="landing-container">
            {/* Hero Section */}
            <header className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">Instant Library System</h1>
                    <p className="hero-subtitle">
                        Experience the next generation of library management.
                        Lightning-fast, cloud-powered, and designed for modern education.
                    </p>
                    <div className="cta-buttons">
                        <button onClick={() => navigate('/register')} className="btn-primary">
                            Get Started
                        </button>
                        <button onClick={() => navigate('/login')} className="btn-secondary">
                            Login
                        </button>
                    </div>
                </div>
            </header>

            {/* Overview Section */}
            <section className="section">
                <h2 className="section-title">Reimagining Library Access</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <span className="feature-icon">⚠️</span>
                        <h3 className="feature-title">The Problem</h3>
                        <p>
                            Traditional libraries struggle with manual tracking, slow searches, and limited accessibility.
                            Students waste time finding books, and staff drown in paperwork.
                        </p>
                    </div>
                    <div className="feature-card">
                        <span className="feature-icon">🚀</span>
                        <h3 className="feature-title">Our Solution</h3>
                        <p>
                            Instant Library brings the catalog to your fingertips.
                            Real-time availability, instant requests, and smart notifications—all powered by the cloud.
                        </p>
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section className="section" style={{ background: '#f9fafb' }}>
                <h2 className="section-title">Why Choose Instant Library?</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <span className="feature-icon">⚡</span>
                        <h3 className="feature-title">Real-Time Updates</h3>
                        <p>Check book availability instantly. No more guessing or wasted trips.</p>
                    </div>
                    <div className="feature-card">
                        <span className="feature-icon">🔔</span>
                        <h3 className="feature-title">Smart Notifications</h3>
                        <p>Get alerted via SNS when your requested book is ready for pickup.</p>
                    </div>
                    <div className="feature-card">
                        <span className="feature-icon">📱</span>
                        <h3 className="feature-title">Accessible Anywhere</h3>
                        <p>Browse the catalog from your dorm, classroom, or on the go.</p>
                    </div>
                </div>
            </section>

            {/* Cloud Architecture Section */}
            <section className="section cloud-section">
                <h2 className="section-title">Powered by AWS Cloud</h2>
                <p className="section-subtitle">Scalable, Secure, and Reliable Infrastructure</p>

                <div className="tech-grid">
                    <div className="tech-item">
                        <div className="tech-icon">💻</div>
                        <h3>Amazon EC2</h3>
                        <p>High-performance computing ensuring 24/7 availability and rapid response times for all users.</p>
                    </div>
                    <div className="tech-item">
                        <div className="tech-icon">🗄️</div>
                        <h3>Amazon DynamoDB</h3>
                        <p>NoSQL database service providing single-digit millisecond latency at any scale.</p>
                    </div>
                    <div className="tech-item">
                        <div className="tech-icon">📨</div>
                        <h3>Amazon SNS</h3>
                        <p>Simple Notification Service delivering immediate email and SMS alerts to students.</p>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <p>&copy; {new Date().getFullYear()} Instant Library Project. All rights reserved.</p>
                <div className="footer-links">
                    <Link to="/privacy">Privacy Policy</Link>
                    <Link to="/terms">Terms of Service</Link>
                    <Link to="/support">Contact Support</Link>
                </div>
            </footer>
        </div>
    );
}

export default Welcome;
