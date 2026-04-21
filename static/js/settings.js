// static/js/settings.js
// Settings panel functionality for Bot Manager

class SettingsManager {
    constructor() {
        this.settings = {
            theme: 'dark',
            apiKey: '',
            model: 'deepseek-chat',
            temperature: 0.7,
            maxTokens: 2048,
            systemPrompt: 'You are a helpful AI assistant. Provide clear, concise, and accurate responses.',
            githubToken: '',
            autoSave: true,
            showTokenUsage: true,
            showResponseTime: true
        };
        
        this.init();
    }
    
    init() {
        this.loadSettings();
        this.bindEvents();
        this.applyTheme();
        this.updateUIFromSettings();
    }
    
    bindEvents() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Save settings button
        const saveSettingsBtn = document.getElementById('saveSettings');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        }
        
        // Reset settings button
        const resetSettingsBtn = document.getElementById('resetSettings');
        if (resetSettingsBtn) {
            resetSettingsBtn.addEventListener('click', () => this.resetSettings());
        }
        
        // Export data button
        const exportDataBtn = document.getElementById('exportData');
        if (exportDataBtn) {
            exportDataBtn.addEventListener('click', () => this.exportData());
        }
        
        // Import data button
        const importDataBtn = document.getElementById('importData');
        if (importDataBtn) {
            importDataBtn.addEventListener('click', () => this.importData());
        }
        
        // Clear all data button
        const clearDataBtn = document.getElementById('clearData');
        if (clearDataBtn) {
            clearDataBtn.addEventListener('click', () => this.clearAllData());
        }
        
        // Push to GitHub button
        const pushToGithubBtn = document.getElementById('pushToGithub');
        if (pushToGithubBtn) {
            pushToGithubBtn.addEventListener('click', () => this.showGithubPushModal());
        }
        
        // GitHub token visibility toggle
        const toggleTokenVisibility = document.getElementById('toggleTokenVisibility');
        if (toggleTokenVisibility) {
            toggleTokenVisibility.addEventListener('click', () => this.toggleTokenVisibility());
        }
        
        // Temperature slider
        const temperatureSlider = document.getElementById('temperature');
        if (temperatureSlider) {
            temperatureSlider.addEventListener('input', (e) => {
                document.getElementById('temperatureValue').textContent = e.target.value;
            });
        }
        
        // Max tokens input
        const maxTokensInput = document.getElementById('maxTokens');
        if (maxTokensInput) {
            maxTokensInput.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                if (value < 100) e.target.value = 100;
                if (value > 4096) e.target.value = 4096;
            });
        }
        
        // Auto-save toggle
        const autoSaveToggle = document.getElementById('autoSave');
        if (autoSaveToggle) {
            autoSaveToggle.addEventListener('change', (e) => {
                this.settings.autoSave = e.target.checked;
                this.saveSettings();
            });
        }
        
        // Show token usage toggle
        const showTokenUsageToggle = document.getElementById('showTokenUsage');
        if (showTokenUsageToggle) {
            showTokenUsageToggle.addEventListener('change', (e) => {
                this.settings.showTokenUsage = e.target.checked;
                this.saveSettings();
            });
        }
        
        // Show response time toggle
        const showResponseTimeToggle = document.getElementById('showResponseTime');
        if (showResponseTimeToggle) {
            showResponseTimeToggle.addEventListener('change', (e) => {
                this.settings.showResponseTime = e.target.checked;
                this.saveSettings();
            });
        }
    }
    
    loadSettings() {
        try {
            const saved = localStorage.getItem('botManagerSettings');
            if (saved) {
                const parsed = JSON.parse(saved);
                this.settings = { ...this.settings, ...parsed };
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showToast('Error loading settings', 'error');
        }
    }
    
    saveSettings() {
        try {
            // Get values from form
            this.settings.apiKey = document.getElementById('apiKey').value;
            this.settings.temperature = parseFloat(document.getElementById('temperature').value);
            this.settings.maxTokens = parseInt(document.getElementById('maxTokens').value);
            this.settings.systemPrompt = document.getElementById('systemPrompt').value;
            this.settings.githubToken = document.getElementById('githubToken').value;
            
            // Save to localStorage
            localStorage.setItem('botManagerSettings', JSON.stringify(this.settings));
            
            // Update API key in app state if exists
            if (window.appState) {
                window.appState.apiKey = this.settings.apiKey;
            }
            
            this.showToast('Settings saved successfully', 'success');
            
            // Dispatch event for other components
            document.dispatchEvent(new CustomEvent('settingsUpdated', {
                detail: { settings: this.settings }
            }));
            
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showToast('Error saving settings', 'error');
        }
    }
    
    resetSettings() {
        if (confirm('Are you sure you want to reset all settings to default?')) {
            try {
                localStorage.removeItem('botManagerSettings');
                this.settings = {
                    theme: 'dark',
                    apiKey: '',
                    model: 'deepseek-chat',
                    temperature: 0.7,
                    maxTokens: 2048,
                    systemPrompt: 'You are a helpful AI assistant. Provide clear, concise, and accurate responses.',
                    githubToken: '',
                    autoSave: true,
                    showTokenUsage: true,
                    showResponseTime: true
                };
                
                this.updateUIFromSettings();
                this.applyTheme();
                this.showToast('Settings reset to default', 'success');
                
            } catch (error) {
                console.error('Error resetting settings:', error);
                this.showToast('Error resetting settings', 'error');
            }
        }
    }
    
    updateUIFromSettings() {
        // Update form fields
        document.getElementById('apiKey').value = this.settings.apiKey;
        document.getElementById('temperature').value = this.settings.temperature;
        document.getElementById('temperatureValue').textContent = this.settings.temperature;
        document.getElementById('maxTokens').value = this.settings.maxTokens;
        document.getElementById('systemPrompt').value = this.settings.systemPrompt;
        document.getElementById('githubToken').value = this.settings.githubToken;
        document.getElementById('autoSave').checked = this.settings.autoSave;
        document.getElementById('showTokenUsage').checked = this.settings.showTokenUsage;
        document.getElementById('showResponseTime').checked = this.settings.showResponseTime;
        
        // Update theme toggle icon
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = this.settings.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }
    
    toggleTheme() {
        this.settings.theme = this.settings.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
        this.saveSettings();
    }
    
    applyTheme() {
        const root = document.documentElement;
        
        if (this.settings.theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        } else {
            root.setAttribute('data-theme', 'light');
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark-theme');
        }
        
        // Update theme toggle icon
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = this.settings.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }
    
    toggleTokenVisibility() {
        const tokenInput = document.getElementById('apiKey');
        const toggleBtn = document.getElementById('toggleTokenVisibility');
        
        if (tokenInput.type === 'password') {
            tokenInput.type = 'text';
            toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            tokenInput.type = 'password';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        }
    }
    
    async exportData() {
        try {
            // Fetch all data from server
            const response = await fetch('/api/export');
            
            if (!response.ok) {
                throw new Error('Failed to export data');
            }
            
            const data = await response.json();
            
            // Create download link
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url