
// Helper to render Sidebar
function renderSidebar(activePath) {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        window.location.href = 'index.html'; // Role selection
        return;
    }

    const isOpen = localStorage.getItem('sidebarOpen') !== 'false'; // Default open

    const studentLinks = [
        { path: 'student_dashboard.html', icon: '🏠', label: 'Dashboard' },
        { path: 'student_dashboard.html#catalog', icon: '📖', label: 'Book Catalog' }, // Assuming catalog is on dash
        { path: '#', icon: '📋', label: 'My Requests' },
        { path: '#', icon: '🔔', label: 'Notifications' },
        { path: '#', icon: '👤', label: 'Profile' }
    ];

    const staffLinks = [
        { path: 'staff_dashboard.html', icon: '📋', label: 'Manage Requests' },
        { path: 'manage_books.html', icon: '📚', label: 'Manage Books' },
        { path: '#', icon: '🎓', label: 'Manage Students' },
        { path: '#', icon: '🔔', label: 'Notifications' },
        { path: '#', icon: '👤', label: 'Profile' }
    ];

    const links = user.role === 'staff' ? staffLinks : studentLinks;

    const html = `
    <aside class="sidebar ${isOpen ? 'open' : 'closed'}" id="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-brand">
                <span class="brand-text">Instant Library</span>
            </div>
            <button class="sidebar-toggle" onclick="toggleSidebar()">
                ${isOpen ? '«' : '☰'}
            </button>
        </div>

        <nav class="sidebar-nav">
            ${links.map(link => `
                <a href="${link.path}" class="nav-link ${activePath === link.path ? 'active' : ''}">
                    <span class="nav-icon">${link.icon}</span>
                    <span class="nav-label">${link.label}</span>
                </a>
            `).join('')}
        </nav>

        <div class="sidebar-footer">
            <div class="user-info">
                <div class="user-name">${user.name}</div>
                <div class="user-role">${user.role === 'staff' ? '👤 Staff' : '🎓 Student'}</div>
            </div>
            <button onclick="logout()" class="logout-btn">
                <span class="logout-icon">🚪</span>
                <span class="logout-text">Logout</span>
            </button>
        </div>
    </aside>
    `;

    document.getElementById('sidebar-container').innerHTML = html;

    // Adjust main container margin
    const appContainer = document.querySelector('.app-container');
    if (appContainer) {
        appContainer.className = `app-container ${isOpen ? 'sidebar-open' : 'sidebar-closed'}`;
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const container = document.querySelector('.app-container');
    const isClosed = sidebar.classList.contains('closed');

    if (isClosed) {
        sidebar.classList.remove('closed');
        sidebar.classList.add('open');
        container.classList.remove('sidebar-closed');
        container.classList.add('sidebar-open');
        localStorage.setItem('sidebarOpen', 'true');
    } else {
        sidebar.classList.remove('open');
        sidebar.classList.add('closed');
        container.classList.remove('sidebar-open');
        container.classList.add('sidebar-closed');
        localStorage.setItem('sidebarOpen', 'false');
    }
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}
