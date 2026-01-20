import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer className="app-footer">
            <p>&copy; {new Date().getFullYear()} Greenfield University. All rights reserved.</p>
            <div className="footer-links">
                <Link to="/privacy" className="footer-link">Privacy Policy</Link>
                <Link to="/terms" className="footer-link">Terms of Service</Link>
                <Link to="/support" className="footer-link">Contact Support</Link>
            </div>
        </footer>
    );
};

export default Footer;
