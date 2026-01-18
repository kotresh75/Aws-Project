/**
 * Instant Library - Core JavaScript Utilities
 * Handles authentication, API calls, and common functions
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api';

// ==================== AUTH UTILITIES ====================

/**
 * Check if user is logged in
 * @returns {object|null} User object or null
 */
function getUser() {
    const userData = localStorage.getItem('user');
    if (userData) {
        try {
            return JSON.parse(userData);
        } catch (e) {
            return null;
        }
    }
    return null;
}

/**
 * Save user to localStorage
 * @param {object} user - User data to save
 */
function saveUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Clear user from localStorage (logout)
 */
function clearUser() {
    localStorage.removeItem('user');
}

/**
 * Check if user is authenticated, redirect to login if not
 * @param {string} redirectUrl - URL to redirect to if not authenticated
 */
function requireAuth(redirectUrl = 'login.html') {
    const user = getUser();
    if (!user) {
        window.location.href = redirectUrl;
        return null;
    }
    return user;
}

/**
 * Check if user has staff role
 * @returns {boolean}
 */
function isStaff() {
    const user = getUser();
    return user && user.role === 'staff';
}

/**
 * Check if user has student role
 * @returns {boolean}
 */
function isStudent() {
    const user = getUser();
    return user && user.role === 'student';
}

/**
 * Logout user and redirect
 */
function logout() {
    clearUser();
    window.location.href = 'login.html';
}

// ==================== API UTILITIES ====================

/**
 * Make API request
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Fetch options
 * @returns {Promise<object>} Response data
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    const response = await fetch(url, mergedOptions);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'API request failed');
    }

    return data;
}

/**
 * GET request helper
 * @param {string} endpoint 
 * @returns {Promise<object>}
 */
async function apiGet(endpoint) {
    return apiRequest(endpoint, { method: 'GET' });
}

/**
 * POST request helper
 * @param {string} endpoint 
 * @param {object} body 
 * @returns {Promise<object>}
 */
async function apiPost(endpoint, body) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
    });
}

/**
 * PUT request helper
 * @param {string} endpoint 
 * @param {object} body 
 * @returns {Promise<object>}
 */
async function apiPut(endpoint, body) {
    return apiRequest(endpoint, {
        method: 'PUT',
        body: JSON.stringify(body),
    });
}

/**
 * DELETE request helper
 * @param {string} endpoint 
 * @param {object} body 
 * @returns {Promise<object>}
 */
async function apiDelete(endpoint, body = {}) {
    return apiRequest(endpoint, {
        method: 'DELETE',
        body: JSON.stringify(body),
    });
}

// ==================== UI UTILITIES ====================

/**
 * Show error message
 * @param {string} message 
 * @param {string} containerId - ID of container element
 */
function showError(message, containerId = 'error-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="error-message">${message}</div>`;
        container.style.display = 'block';
    }
}

/**
 * Show success message
 * @param {string} message 
 * @param {string} containerId - ID of container element
 */
function showSuccess(message, containerId = 'success-container') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="success-message">${message}</div>`;
        container.style.display = 'block';
    }
}

/**
 * Hide message container
 * @param {string} containerId 
 */
function hideMessage(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
}

/**
 * Show loading state on button
 * @param {HTMLElement} button 
 * @param {string} loadingText 
 */
function setButtonLoading(button, loadingText = 'Loading...') {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = loadingText;
}

/**
 * Reset button from loading state
 * @param {HTMLElement} button 
 */
function resetButton(button) {
    button.disabled = false;
    if (button.dataset.originalText) {
        button.textContent = button.dataset.originalText;
    }
}

/**
 * Format date to DD/MM/YYYY
 * @param {string} dateString 
 * @returns {string}
 */
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

/**
 * Get current page name from URL
 * @returns {string}
 */
function getCurrentPage() {
    const path = window.location.pathname;
    const page = path.substring(path.lastIndexOf('/') + 1);
    return page || 'index.html';
}

// ==================== NAVIGATION ====================

/**
 * Navigate to page
 * @param {string} page 
 */
function navigateTo(page) {
    window.location.href = page;
}

// ==================== SIDEBAR UTILITIES ====================

/**
 * Get sidebar state from localStorage
 * @returns {boolean}
 */
function getSidebarState() {
    const state = localStorage.getItem('sidebarOpen');
    return state === null ? true : state === 'true';
}

/**
 * Save sidebar state to localStorage
 * @param {boolean} isOpen 
 */
function saveSidebarState(isOpen) {
    localStorage.setItem('sidebarOpen', String(isOpen));
}
