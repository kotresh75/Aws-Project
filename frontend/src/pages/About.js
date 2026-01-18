import React from 'react';


function About() {
    return (
        <>

            <div className="about-container" style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
                <div className="about-content" style={{ backgroundColor: 'white', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
                    <div className="about-header" style={{ marginBottom: '30px', borderBottom: '2px solid #f3f4f6', paddingBottom: '20px' }}>
                        <h1 style={{ fontSize: '2.5rem', color: '#111827', marginBottom: '10px' }}>Greenfield University Instant Library</h1>
                        <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>Empowering students with seamless access to educational resources.</p>
                    </div>

                    <div className="about-section" style={{ marginBottom: '40px' }}>
                        <h2 style={{ fontSize: '1.5rem', color: '#374151', marginBottom: '15px' }}>Our Mission</h2>
                        <p style={{ lineHeight: '1.8', color: '#4b5563', marginBottom: '15px' }}>
                            At Greenfield University, the BSC Computer Science department faces a shortage of physical textbooks due to a growing student population.
                            The limited availability of library resources has led to long wait times and challenges in accessing essential study materials.
                        </p>
                        <p style={{ lineHeight: '1.8', color: '#4b5563' }}>
                            To solve this, the university’s Cloud Solutions Department developed the <strong>Instant Library</strong>—a virtual library platform.
                            This cloud-based solution enhances the availability of study materials, providing seamless access for all students.
                        </p>
                    </div>

                    <div className="about-features" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', marginBottom: '40px' }}>
                        <div className="feature-card" style={{ padding: '25px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
                            <h3 style={{ fontSize: '1.25rem', color: '#1f2937', marginBottom: '10px' }}>🚀 Cloud Powered</h3>
                            <p style={{ color: '#6b7280' }}>
                                Using Flask for backend development, AWS EC2 for hosting, and DynamoDB for managing data, the system ensures high availability and scalability.
                            </p>
                        </div>
                        <div className="feature-card" style={{ padding: '25px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
                            <h3 style={{ fontSize: '1.25rem', color: '#1f2937', marginBottom: '10px' }}>🔔 Real-time Notifications</h3>
                            <p style={{ color: '#6b7280' }}>
                                AWS SNS sends real-time notifications to students and library staff about requests, ensuring effective communication and resource management.
                            </p>
                        </div>
                        <div className="feature-card" style={{ padding: '25px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
                            <h3 style={{ fontSize: '1.25rem', color: '#1f2937', marginBottom: '10px' }}>📚 Seamless Access</h3>
                            <p style={{ color: '#6b7280' }}>
                                The system allows students to register, log in, and request books online, removing barriers to essential learning materials.
                            </p>
                        </div>
                    </div>

                    <div className="about-footer" style={{ textAlign: 'center', marginTop: '60px', paddingTop: '20px', borderTop: '1px solid #e5e7eb' }}>
                        <p style={{ color: '#9ca3af', fontSize: '0.9rem' }}>© {new Date().getFullYear()} Greenfield University. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </>
    );
}

export default About;
