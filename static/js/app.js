// static/js/app.js
// Main application logic for Bot Manager

class BotManagerApp {
    constructor() {
        this.currentBot = null;
        this.currentChat = [];
        this.bots = [];
        this.settings = {};
        this.isDarkMode = false;
        this.apiStatus = 'unknown';
        this.init();
    }

    async init() {
        // Load settings from localStorage
        this.loadSettings();
        
        // Initialize theme
        this.initTheme();
        
        // Initialize event listeners
        this.initEventListeners();
        
        // Load initial data
        await this.loadBots();
        await this.checkApiStatus();
        
        // Initialize modules
        this.initChat();
        this.initBots();
        this.initAnalytics();
        
        // Update UI
        this.updateUI();
        
        // Start periodic status checks
        this.startStatusChecks();
    }

    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('botManagerSettings');
            if (savedSettings) {
                this.settings = JSON.parse(savedSettings);
            } else {
                this.settings = {
                    apiKey: '',
                    temperature: 0.7,
                    maxTokens: 2048,
                    defaultPrompt: 'You are a helpful AI assistant.',
                    githubToken: '',
                    theme: 'dark'
                };
            }
            
            // Load theme preference
            const savedTheme = localStorage.getItem('theme');
            this.isDarkMode = savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
        } catch (error) {
            console.error('Error loading settings:', error);
            this.settings = {
                apiKey: '',
                temperature: 0.7,
                maxTokens: 2048,
                defaultPrompt: 'You are a helpful AI assistant.',
                githubToken: '',
                theme: 'dark'
            };
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('botManagerSettings', JSON.stringify(this.settings));
            localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    initTheme() {
        if (this.isDarkMode) {
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        } else {
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        }
        
        // Update theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.innerHTML = this.isDarkMode ? 
                '<i class="fas fa-sun"></i> Light Mode' : 
                '<i class="fas fa-moon"></i> Dark Mode';
        }
    }

    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        this.initTheme();
        this.saveSettings();
    }

    initEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.showSection(section);
            });
        });

        // Create bot button
        const createBotBtn = document.getElementById('createBotBtn');
        if (createBotBtn) {
            createBotBtn.addEventListener('click', () => {
                if (window.botManager) {
                    window.botManager.showBotModal();
                }
            });
        }

        // Bot search
        const botSearch = document.getElementById('botSearch');
        if (botSearch) {
            botSearch.addEventListener('input', (e) => {
                if (window.botManager) {
                    window.botManager.filterBots(e.target.value);
                }
            });
        }

        // Settings save
        const saveSettingsBtn = document.getElementById('saveSettings');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => this.saveSettingsFromForm());
        }

        // GitHub push
        const pushToGithubBtn = document.getElementById('pushToGithub');
        if (pushToGithubBtn) {
            pushToGithubBtn.addEventListener('click', () => this.pushToGithub());
        }

        // Clear all data
        const clearDataBtn = document.getElementById('clearDataBtn');
        if (clearDataBtn) {
            clearDataBtn.addEventListener('click', () => this.clearAllData());
        }

        // Import/Export
        const exportDataBtn = document.getElementById('exportDataBtn');
        if (exportDataBtn) {
            exportDataBtn.addEventListener('click', () => this.exportData());
        }

        const importDataBtn = document.getElementById('importDataBtn');
        if (importDataBtn) {
            importDataBtn.addEventListener('change', (e) => this.importData(e));
        }

        // Window events
        window.addEventListener('botCreated', () => this.handleBotCreated());
        window.addEventListener('botUpdated', () => this.handleBotUpdated());
        window.addEventListener('botDeleted', () => this.handleBotDeleted());
        window.addEventListener('chatUpdated', () => this.handleChatUpdated());
    }

    async loadBots() {
        try {
            const response = await fetch('/api/bots');
            if (response.ok) {
                this.bots = await response.json();
                this.updateBotList();
            } else {
                throw new Error('Failed to load bots');
            }
        } catch (error) {
            console.error('Error loading bots:', error);
            this.showToast('Error loading bots', 'error');
        }
    }

    async checkApiStatus() {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                this.apiStatus = 'online';
            } else {
                this.apiStatus = 'offline';
            }
        } catch (error) {
            this.apiStatus = 'offline';
        }
        this.updateApiStatus();
    }

    updateApiStatus() {
        const statusElement = document.getElementById('apiStatus');
        if (statusElement) {
            statusElement.innerHTML = this.apiStatus === 'online' ?
                '<i class="fas fa-circle-check" style="color: #10b981;"></i> API Online' :
                '<i class="fas fa-circle-xmark" style="color: #ef4444;"></i> API Offline';
        }
    }

    updateBotList() {
        if (window.botManager) {
            window.botManager.renderBotList(this.bots);
        }
    }

    showSection(section) {
        // Hide all sections
        document.querySelectorAll('.main-section').forEach(sec => {
            sec.classList.remove('active');
        });

        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(`${section}Section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Activate nav item
        const navItem = document.querySelector(`.nav-item[data-section="${section}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }

        // Load section-specific data
        switch(section) {
            case 'analytics':
                if (window.analyticsManager) {
                    window.analyticsManager.loadAnalytics();
                }
                break;
            case 'settings':
                this.loadSettingsToForm();
                break;
        }
    }

    loadSettingsToForm() {
        const apiKeyInput = document.getElementById('apiKey');
        const temperatureInput = document.getElementById('temperature');
        const maxTokensInput = document.getElementById('maxTokens');
        const defaultPromptInput = document.getElementById('defaultPrompt');
        const githubTokenInput = document.getElementById('githubToken');
        const temperatureValue = document.getElementById('temperatureValue');
        const maxTokensValue = document.getElementById('maxTokensValue');

        if (apiKeyInput) {
            apiKeyInput.value = this.settings.apiKey || '';
        }
        if (temperatureInput) {
            temperatureInput.value = this.settings.temperature || 0.7;
        }
        if (temperatureValue) {
            temperatureValue.textContent = this.settings.temperature || 0.7;
        }
        if (maxTokensInput) {
            maxTokensInput.value = this.settings.maxTokens || 2048;
        }
        if (maxTokensValue) {
            maxTokensValue.textContent = this.settings.maxTokens || 2048;
        }
        if (defaultPromptInput) {
            defaultPromptInput.value = this.settings.defaultPrompt || 'You are a helpful AI assistant.';
        }
        if (githubTokenInput) {
            githubTokenInput.value = this.settings.githubToken || '';
        }
    }

    saveSettingsFromForm() {
        const apiKeyInput = document.getElementById('apiKey');
        const temperatureInput = document.getElementById('temperature');
        const maxTokensInput = document.getElementById('maxTokens');
        const defaultPromptInput = document.getElementById('defaultPrompt');
        const githubTokenInput = document.getElementById('githubToken');

        if (apiKeyInput) {
            this.settings.apiKey = apiKeyInput.value.trim();
        }
        if (temperature