import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/LandingPage.css'; // Reusing Landing Page styles for Nav/Hero

function About() {
    const navigate = useNavigate();

    return (
        <div className="landing-container">
            {/* Navigation Bar */}
            <nav className="landing-nav">
                <div className="nav-content">
                    <div className="nav-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
                        <span className="logo-icon">📚</span>
                        <span className="logo-text">Instant Library</span>
                    </div>
                    <div className="nav-links">
                        <Link to="/" className="nav-link">Home</Link>
                        <Link to="/login" className="nav-link">Login</Link>
                        <Link to="/register" className="btn-primary small">Get Started</Link>
                    </div>
                </div>
            </nav>

            {/* Header/Hero for About Page */}
            <header className="hero-section" style={{ padding: '8rem 2rem 4rem', minHeight: 'auto' }}>
                <div className="hero-content">
                    <div className="hero-badge">About Us</div>
                    <h1 className="hero-title" style={{ fontSize: '3.5rem' }}>
                        Empowering <span className="gradient-text">Education</span>
                    </h1>
                    <p className="hero-subtitle">
                        Greenfield University's Cloud-Powered Library System.
                        Seamless access to educational resources for every student.
                    </p>
                </div>
            </header>

            {/* Main Content */}
            <div className="page-container" style={{ maxWidth: '1000px', margin: '0 auto', paddingBottom: '4rem' }}>

                {/* Mission Section */}
                <div className="glass-card" style={{ marginBottom: '3rem', padding: '3rem' }}>
                    <h2 style={{ fontSize: '2rem', marginBottom: '1.5rem', color: 'var(--primary-dark)' }}>Our Mission</h2>
                    <p style={{ fontSize: '1.1rem', lineHeight: '1.8', color: 'var(--text-main)', marginBottom: '1.5rem' }}>
                        At Greenfield University, the BSC Computer Science department faces a shortage of physical textbooks due to a growing student population.
                        The limited availability of library resources has led to long wait times and challenges in accessing essential study materials.
                    </p>
                    <p style={{ fontSize: '1.1rem', lineHeight: '1.8', color: 'var(--text-main)' }}>
                        To solve this, the university’s Cloud Solutions Department developed the <strong>Instant Library</strong>—a virtual library platform.
                        Using Flask, AWS EC2, and DynamoDB, this cloud-based solution allows students to register, log in, and request books online,
                        enhancing the availability of study materials and providing seamless access for all students.
                    </p>
                </div>

                {/* Scenarios Section */}
                <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '2rem' }}>Key Usage Scenarios</h2>

                <div style={{ display: 'grid', gap: '2rem' }}>

                    <div className="glass-card" style={{ borderLeft: '5px solid var(--info)' }}>
                        <h3 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.8rem' }}>🚀</span> Efficient Book Requests
                        </h3>
                        <p style={{ color: 'var(--text-muted)', lineHeight: '1.7' }}>
                            AWS EC2 ensures a reliable infrastructure to manage multiple students. A student can log in, navigate to the book request page,
                            and easily submit a request for unavailable textbooks. The cloud-based architecture allows the platform to handle a high volume
                            of requests during peak periods smoothy.
                        </p>
                    </div>

                    <div className="glass-card" style={{ borderLeft: '5px solid var(--success)' }}>
                        <h3 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.8rem' }}>🔔</span> Seamless Notifications
                        </h3>
                        <p style={{ color: 'var(--text-muted)', lineHeight: '1.7' }}>
                            When students request books, the system uses AWS SNS to notify both students and library staff.
                            Flask processes the request while SNS sends an email confirmation. The secure integration with AWS DynamoDB
                            ensures all requests are tracked and resolved efficiently.
                        </p>
                    </div>

                    <div className="glass-card" style={{ borderLeft: '5px solid var(--primary)' }}>
                        <h3 style={{ fontSize: '1.4rem', color: 'var(--text-main)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.8rem' }}>📱</span> Easy Resource Access
                        </h3>
                        <p style={{ color: 'var(--text-muted)', lineHeight: '1.7' }}>
                            Students can quickly check availability status or place requests if a book is not in stock.
                            Flask manages real-time data fetching, while EC2 hosting ensures the platform performs seamlessly
                            even when multiple students access it simultaneously.
                        </p>
                    </div>
                </div>

                {/* Tech Stack Grid */}
                <div style={{ marginTop: '4rem' }}>
                    <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '2rem' }}>Built on AWS</h2>
                    <div className="features-grid">
                        <div className="feature-card" style={{ textAlign: 'center' }}>
                            <div className="feature-icon">☁️</div>
                            <h3>Amazon EC2</h3>
                            <p>Scalable Compute</p>
                        </div>
                        <div className="feature-card" style={{ textAlign: 'center' }}>
                            <div className="feature-icon">🗄️</div>
                            <h3>DynamoDB</h3>
                            <p>NoSQL Database</p>
                        </div>
                        <div className="feature-card" style={{ textAlign: 'center' }}>
                            <div className="feature-icon">📨</div>
                            <h3>Amazon SNS</h3>
                            <p>Notifications</p>
                        </div>
                    </div>
                </div>

            </div>

            {/* Footer */}
            <footer className="landing-footer">
                <p>&copy; {new Date().getFullYear()} Greenfield University. All rights reserved.</p>
                <div className="footer-links">
                    <Link to="/privacy">Privacy Policy</Link>
                    <Link to="/terms">Terms of Service</Link>
                    <Link to="/support">Contact Support</Link>
                </div>
            </footer>
        </div>
    );
}

export default About;
