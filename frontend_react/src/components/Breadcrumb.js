import React from 'react';
import { useLocation, Link } from 'react-router-dom';

const Breadcrumb = ({ pageTitle }) => {
    const location = useLocation();

    const getBreadcrumbItems = () => {
        const routeMap = {
            '/dashboard': 'Dashboard',
            '/catalog': 'Book Catalog',
            '/requests': 'My Requests',
            '/book-management': 'Manage Books',
            '/request-management': 'Manage Requests',
            '/student-management': 'Student Management',
            '/staff-management': 'Staff Management',
            '/profile': 'Profile',
            '/settings': 'Settings',
            '/notifications': 'Notifications',
            '/request-history': 'Request History',
            '/about': 'About'
        };

        const items = [
            { label: 'Dashboard', path: '/dashboard' }
        ];

        const pathname = location.pathname;

        // If we are on dashboard, return just the dashboard item
        if (pathname === '/dashboard') {
            return items;
        }

        const mappedLabel = routeMap[pathname];

        if (mappedLabel) {
            // If path is known, use the mapped label (ignore pageTitle to avoid duplicates)
            items.push({ label: mappedLabel, path: pathname });
        } else if (pageTitle) {
            // Fallback to pageTitle for unknown routes
            items.push({ label: pageTitle, path: pathname });
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
        </div>
    );
};

export default Breadcrumb;
