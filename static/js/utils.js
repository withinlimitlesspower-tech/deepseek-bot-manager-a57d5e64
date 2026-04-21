// static/js/utils.js
// Utility functions for Bot Manager application

class Utils {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.toastContainer = null;
        this.initToastContainer();
    }

    /**
     * Initialize toast notification container
     */
    initToastContainer() {
        if (!this.toastContainer) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.className = 'toast-container';
            document.body.appendChild(this.toastContainer);
        }
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of toast (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                ${this.getToastIcon(type)}
            </div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);

        return toast;
    }

    /**
     * Get icon for toast type
     * @param {string} type - Toast type
     * @returns {string} - HTML icon
     */
    getToastIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        return icons[type] || icons.info;
    }

    /**
     * Make API request with error handling
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {object} data - Request data
     * @param {object} headers - Additional headers
     * @returns {Promise<object>} - Response data
     */
    async apiRequest(endpoint, method = 'GET', data = null, headers = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            credentials: 'same-origin'
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            this.showToast(`API Error: ${error.message}`, 'error');
            throw error;
        }
    }

    /**
     * Format date to readable string
     * @param {Date|string} date - Date to format
     * @param {boolean} includeTime - Whether to include time
     * @returns {string} - Formatted date
     */
    formatDate(date, includeTime = true) {
        const d = new Date(date);
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };

        if (includeTime) {
            options.hour = '2-digit';
            options.minute = '2-digit';
        }

        return d.toLocaleDateString('en-US', options);
    }

    /**
     * Format timestamp for chat messages
     * @param {Date|string} date - Date to format
     * @returns {string} - Formatted time
     */
    formatTime(date) {
        const d = new Date(date);
        return d.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Truncate text with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} - Truncated text
     */
    truncateText(text, maxLength = 50) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Generate random ID
     * @param {number} length - Length of ID
     * @returns {string} - Random ID
     */
    generateId(length = 8) {
        return Math.random().toString(36).substring(2, 2 + length);
    }

    /**
     * Debounce function to limit rate of execution
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} - Debounced function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Throttle function to limit execution rate
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} - Throttled function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} - Whether email is valid
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Validate repository name
     * @param {string} repoName - Repository name to validate
     * @returns {boolean} - Whether repo name is valid
     */
    validateRepoName(repoName) {
        const re = /^[a-z0-9_.-]+$/;
        return re.test(repoName);
    }

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} - Success status
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!', 'success');
            return true;
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showToast('Failed to copy to clipboard', 'error');
            return false;
        }
    }

    /**
     * Download file from content
     * @param {string} content - File content
     * @param {string} filename - File name
     * @param {string} type - MIME type
     */
    downloadFile(content, filename, type = 'text/plain') {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Read file as text
     * @param {File} file - File to read
     * @returns {Promise<string>} - File content
     */
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    }

    /**
     * Parse JSON safely
     * @param {string} jsonString - JSON string to parse
     * @returns {object|null} - Parsed object or null
     */
    safeJsonParse(jsonString) {
        try {
            return JSON.parse(jsonString);
        } catch (error) {
            console.error('Failed to parse JSON:', error);
            return null;
        }
    }

    /**
     * Stringify JSON with formatting
     * @param {object} data - Data to stringify
     * @returns {string} - Formatted JSON string
     */
    prettyJson(data) {
        return JSON.stringify(data