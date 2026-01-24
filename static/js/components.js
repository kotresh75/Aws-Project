/**
 * Header and Footer Components
 * Dynamically injects header and footer into protected pages
 */

// Page title mapping for breadcrumb
const pageTitles = {
    'dashboard.html': 'Dashboard',
    'catalog.html': 'Book Catalog',
    'requests.html': 'My Requests',
    'profile.html': 'Profile',
    'settings.html': 'Settings',
    'notifications.html': 'Notifications',
    'about.html': 'About',
    'book-management.html': 'Manage Books',
    'request-management.html': 'Manage Requests',
    'student-management.html': 'Manage Students',
    'staff-management.html': 'Add Staff',
};

/**
 * Initialize header component
 */
function initHeader() {
    const user = getUser();
    if (!user) return;

    const currentPage = getCurrentPage();
    const pageTitle = pageTitles[currentPage] || 'Page';

    const headerHTML = `
        <header class="app-header">
            <div class="header-left">
                <nav class="breadcrumb">
                    <a href="dashboard.html">🏠 Home</a>
                    <span class="breadcrumb-separator">›</span>
                    <span class="breadcrumb-current">${pageTitle}</span>
                </nav>
            </div>
            <div class="header-right">
                <a href="profile.html" class="user-profile-preview">
                    <span class="user-greeting">Hello, <strong>${user.name || 'User'}</strong></span>
                    <div class="user-avatar">${user.name ? user.name.charAt(0).toUpperCase() : 'U'}</div>
                </a>
            </div>
        </header>
    `;

    // Insert header at the beginning of main
    const main = document.querySelector('main');
    if (main) {
        main.insertAdjacentHTML('afterbegin', headerHTML);
    }
}

/**
 * Initialize footer component
 */
function initFooter() {
    const footerHTML = `
        <footer class="app-footer">
            <p>&copy; ${new Date().getFullYear()} Greenfield University. All rights reserved.</p>
            <div class="footer-links">
                <a href="privacy.html" class="footer-link">Privacy Policy</a>
                <a href="terms.html" class="footer-link">Terms of Service</a>
                <a href="support.html" class="footer-link">Contact Support</a>
            </div>
        </footer>
    `;

    // Insert footer at the end of main or app-container
    const main = document.querySelector('main');
    if (main) {
        main.insertAdjacentHTML('afterend', footerHTML);
    }
}

/**
 * Initialize both header and footer
 * Call this on protected pages
 */
function initHeaderFooter() {
    initHeader();
    initFooter();
}

// Auto-initialize when DOM is ready (for protected pages with app-container)
document.addEventListener('DOMContentLoaded', function () {
    if (document.querySelector('.app-container')) {
        initHeaderFooter();

        // Dynamic Chatbot Injection
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'styles/chatbot.css';
        document.head.appendChild(cssLink);

        const jsScript = document.createElement('script');
        jsScript.src = 'js/chatbot.js';
        document.body.appendChild(jsScript);
    }
});
