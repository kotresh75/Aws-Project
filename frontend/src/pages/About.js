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
                            At Greenfield University, the BSC Computer Science department faces a shortage of physical textbooks due to a growing student population. The limited availability of library resources has led to long wait times and challenges in accessing essential study materials.
                        </p>
                        <p style={{ lineHeight: '1.8', color: '#4b5563' }}>
                            To solve this, the university’s Cloud Solutions Department developed the Instant Library—a virtual library platform. Using Flask for backend development, AWS EC2 for hosting, and DynamoDB for managing data, the system allows students to register, log in, and request books online. AWS SNS sends real-time notifications to students and library staff about requests, ensuring effective communication and resource management. This cloud-based solution enhances the availability of study materials, providing seamless access for all students.
                        </p>
                    </div>

                    <div className="scenarios-section" style={{ marginBottom: '40px' }}>
                        <h2 style={{ fontSize: '1.5rem', color: '#374151', marginBottom: '15px' }}>Usage Scenarios</h2>

                        <div className="scenario-card" style={{ marginBottom: '20px', padding: '20px', backgroundColor: '#fff', borderLeft: '4px solid #3b82f6', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                            <h3 style={{ fontSize: '1.2rem', color: '#1f2937', marginBottom: '10px' }}>Scenario 1: Efficient Book Request System for Students</h3>
                            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
                                In the Instant Library System at Greenfield University, AWS EC2 ensures a reliable infrastructure to manage multiple students accessing the platform simultaneously. For example, a student can log in, navigate to the book request page, and easily submit a request for unavailable textbooks. Flask handles backend operations, efficiently retrieving and processing user data in real-time. The cloud-based architecture allows the platform to handle a high volume of book requests during peak periods, ensuring smooth operation without delays.
                            </p>
                        </div>

                        <div className="scenario-card" style={{ marginBottom: '20px', padding: '20px', backgroundColor: '#fff', borderLeft: '4px solid #10b981', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                            <h3 style={{ fontSize: '1.2rem', color: '#1f2937', marginBottom: '10px' }}>Scenario 2: Seamless Book Request Notifications for Library Staff</h3>
                            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
                                When students request books that are unavailable in the physical library, the Instant Library System uses AWS SNS to notify both the students and the library staff. For instance, a student requests a textbook, and Flask processes the request while SNS sends an email to both the student (confirming the request) and the library staff (informing them of the new request). The secure integration with AWS DynamoDB stores all book requests, ensuring they are tracked and resolved efficiently.
                            </p>
                        </div>

                        <div className="scenario-card" style={{ marginBottom: '20px', padding: '20px', backgroundColor: '#fff', borderLeft: '4px solid #8b5cf6', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                            <h3 style={{ fontSize: '1.2rem', color: '#1f2937', marginBottom: '10px' }}>Scenario 3: Easy Access to Library Resources</h3>
                            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
                                The Instant Library System provides students with easy access to available resources in the library. For example, a student logs in and views the list of available books and materials on the platform. They can quickly check the availability status or place a request if the book is not in stock. Flask manages real-time data fetching from DynamoDB, while EC2 hosting ensures the platform performs seamlessly even when multiple students access it at the same time, offering a smooth and uninterrupted user experience.
                            </p>
                        </div>
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
