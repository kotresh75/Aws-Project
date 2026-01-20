import React from 'react';
import Breadcrumb from './Breadcrumb';
import '../styles/Header.css';

const Header = () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    return (
        <header className="app-header">
            <div className="header-left">
                <Breadcrumb />
            </div>
            <div className="header-right">
                <div className="user-profile-preview">
                    <span className="user-greeting">Hello, <strong>{user.name || 'User'}</strong></span>
                    <div className="user-avatar-placeholder">
                        {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
