import React from 'react';
import { useLocation, Link } from 'react-router-dom';

const Breadcrumb = ({ pageTitle }) => {
    const location = useLocation();

    const getBreadcrumbItems = () => {
        // Default home item
        const items = [
            { label: 'Dashboard', path: '/dashboard' }
        ];

        // Add current page based on location
        const pathname = location.pathname;

        if (pathname.includes('/book-catalog')) {
            items.push({ label: 'Book Catalog', path: '/book-catalog' });
        } else if (pathname.includes('/request-history')) {
            items.push({ label: 'Request History', path: '/request-history' });
        } else if (pathname.includes('/book-management')) {
            items.push({ label: 'Book Management', path: '/book-management' });
        } else if (pathname.includes('/request-management')) {
            items.push({ label: 'Request Management', path: '/request-management' });
        } else if (pathname.includes('/profile')) {
            items.push({ label: 'Profile', path: '/profile' });
        } else if (pathname.includes('/settings')) {
            items.push({ label: 'Settings', path: '/settings' });
        } else if (pathname.includes('/notifications')) {
            items.push({ label: 'Notifications', path: '/notifications' });
        } else if (pathname.includes('/staff-management')) {
            items.push({ label: 'Staff Management', path: '/staff-management' });
        }

        return items;
    };

    const breadcrumbItems = getBreadcrumbItems();

    return (
        <div className="breadcrumb">
            {breadcrumbItems.map((item, index) => (
                <div key={index} className="breadcrumb-item">
                    {index < breadcrumbItems.length - 1 ? (
                        <>
                            <Link to={item.path}>{item.label}</Link>
                            <span className="breadcrumb-separator">/</span>
                        </>
                    ) : (
                        <span className="active">{item.label}</span>
                    )}
                </div>
            ))}
            {pageTitle && (
                <>
                    <span className="breadcrumb-separator">/</span>
                    <div className="breadcrumb-item">
                        <span className="active">{pageTitle}</span>
                    </div>
                </>
            )}
        </div>
    );
};

export default Breadcrumb;
