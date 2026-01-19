/**
 * Sidebar Component JavaScript
 * Handles sidebar rendering and toggle functionality
 */

// Student navigation links
const studentLinks = [
    { path: 'dashboard.html', icon: '🏠', label: 'Dashboard' },
    { path: 'catalog.html', icon: '📖', label: 'Book Catalog' },
    { path: 'requests.html', icon: '📋', label: 'My Requests' },
    { path: 'notifications.html', icon: '🔔', label: 'Notifications' },
    { path: 'profile.html', icon: '👤', label: 'Profile' },
    { path: 'settings.html', icon: '⚙️', label: 'Settings' },
];

// Staff navigation links
const staffLinks = [
    { path: 'dashboard.html', icon: '🏠', label: 'Dashboard' },
    { path: 'book-management.html', icon: '📚', label: 'Manage Books' },
    { path: 'request-management.html', icon: '📋', label: 'Manage Requests' },
    { path: 'student-management.html', icon: '🎓', label: 'Manage Students' },
    { path: 'staff-management.html', icon: '👥', label: 'Add Staff' },
    { path: 'notifications.html', icon: '🔔', label: 'Notifications' },
    { path: 'profile.html', icon: '👤', label: 'Profile' },
    { path: 'settings.html', icon: '⚙️', label: 'Settings' },
];

/**
 * Initialize sidebar
 * Call this function on pages that need the sidebar
 */
function initSidebar() {
    const user = getUser();
    if (!user) {
        return; // Don't render sidebar if not logged in
    }

    const navLinks = user.role === 'staff' ? staffLinks : studentLinks;
    const currentPage = getCurrentPage();
    const isOpen = getSidebarState();

    renderSidebar(user, navLinks, currentPage, isOpen);
    setupSidebarEvents();
    updateAppContainerClass(isOpen);
}

/**
 * Render sidebar HTML
 */
function renderSidebar(user, navLinks, currentPage, isOpen) {
    const sidebarHTML = `
        <aside class="sidebar ${isOpen ? 'open' : 'closed'}" id="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-brand">
                    ${isOpen ? '<span class="brand-text">Instant Library</span>' : ''}
                </div>
                <button class="sidebar-toggle" id="sidebar-toggle">
                    ${isOpen ? '«' : '☰'}
                </button>
            </div>

            <nav class="sidebar-nav">
                ${navLinks.map(link => `
                    <a href="${link.path}" 
                       class="nav-link ${currentPage === link.path ? 'active' : ''}"
                       title="${!isOpen ? link.label : ''}">
                        <span class="nav-icon">${link.icon}</span>
                        ${isOpen ? `<span class="nav-label">${link.label}</span>` : ''}
                    </a>
                `).join('')}
            </nav>

            <div class="sidebar-footer">
                <div class="user-info" ${!isOpen ? 'style="display:none"' : ''}>
                    <div class="user-name">${user.name}</div>
                    <div class="user-role">
                        ${user.role === 'staff' ? '👤 Staff' : '🎓 Student'}
                    </div>
                </div>
                <button class="logout-btn" id="logout-btn" title="${!isOpen ? 'Logout' : ''}">
                    <span class="logout-icon">🚪</span>
                    ${isOpen ? '<span class="logout-text">Logout</span>' : ''}
                </button>
            </div>
        </aside>
        <div class="sidebar-overlay" id="sidebar-overlay"></div>
    `;

    // Insert at beginning of body
    document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
}

/**
 * Setup sidebar event listeners
 */
function setupSidebarEvents() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const logoutBtn = document.getElementById('logout-btn');
    const overlay = document.getElementById('sidebar-overlay');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleSidebar);
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    if (overlay) {
        overlay.addEventListener('click', toggleSidebar);
    }
}

/**
 * Toggle sidebar open/closed
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const isCurrentlyOpen = sidebar.classList.contains('open');
    const newState = !isCurrentlyOpen;

    // Update sidebar classes
    sidebar.classList.toggle('open', newState);
    sidebar.classList.toggle('closed', !newState);

    // Update overlay for mobile
    if (overlay) {
        overlay.classList.toggle('visible', newState);
    }

    // Update toggle button text
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (toggleBtn) {
        toggleBtn.textContent = newState ? '«' : '☰';
    }

    // Update brand text
    const brand = sidebar.querySelector('.sidebar-brand');
    if (brand) {
        brand.innerHTML = newState ? '<span class="brand-text">Instant Library</span>' : '';
    }

    // Update nav labels
    const navLabels = sidebar.querySelectorAll('.nav-label');
    navLabels.forEach(label => {
        label.style.display = newState ? '' : 'none';
    });

    // Update user info
    const userInfo = sidebar.querySelector('.user-info');
    if (userInfo) {
        userInfo.style.display = newState ? '' : 'none';
    }

    // Update logout text
    const logoutText = sidebar.querySelector('.logout-text');
    if (logoutText) {
        logoutText.style.display = newState ? '' : 'none';
    }

    // Update nav link titles
    const navLinks = sidebar.querySelectorAll('.nav-link');
    const currentLinks = getUser()?.role === 'staff' ? staffLinks : studentLinks;
    navLinks.forEach((link, index) => {
        link.title = !newState ? currentLinks[index]?.label || '' : '';
    });

    // Save state and update container
    saveSidebarState(newState);
    updateAppContainerClass(newState);
}

/**
 * Update app container class based on sidebar state
 */
function updateAppContainerClass(isOpen) {
    const container = document.querySelector('.app-container');
    if (container) {
        container.classList.toggle('sidebar-open', isOpen);
        container.classList.toggle('sidebar-closed', !isOpen);
    }
}

// Auto-initialize sidebar when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    // Only init sidebar if we're on a protected page (has app-container)
    if (document.querySelector('.app-container')) {
        initSidebar();
    }
});
