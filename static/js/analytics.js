// static/js/analytics.js
// Analytics dashboard with Chart.js visualizations and statistics

class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.stats = {};
        this.init();
    }

    async init() {
        await this.loadStats();
        this.renderStatsCards();
        this.initCharts();
        this.loadRecentActivity();
        this.setupEventListeners();
    }

    async loadStats() {
        try {
            const response = await fetch('/api/analytics/stats');
            if (!response.ok) throw new Error('Failed to load analytics');
            this.stats = await response.json();
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.stats = {
                totalBots: 0,
                activeBots: 0,
                messagesToday: 0,
                tokensUsed: 0,
                messagesPerDay: [],
                tokenUsageByBot: [],
                recentActivity: []
            };
        }
    }

    renderStatsCards() {
        const cards = document.querySelectorAll('.stat-card');
        if (!cards.length) return;

        // Total Bots
        const totalBotsCard = document.querySelector('[data-stat="total-bots"]');
        if (totalBotsCard) {
            totalBotsCard.querySelector('.stat-number').textContent = this.stats.totalBots || 0;
        }

        // Active Bots
        const activeBotsCard = document.querySelector('[data-stat="active-bots"]');
        if (activeBotsCard) {
            activeBotsCard.querySelector('.stat-number').textContent = this.stats.activeBots || 0;
        }

        // Messages Today
        const messagesCard = document.querySelector('[data-stat="messages-today"]');
        if (messagesCard) {
            messagesCard.querySelector('.stat-number').textContent = this.stats.messagesToday || 0;
        }

        // Tokens Used
        const tokensCard = document.querySelector('[data-stat="tokens-used"]');
        if (tokensCard) {
            tokensCard.querySelector('.stat-number').textContent = this.formatNumber(this.stats.tokensUsed || 0);
        }
    }

    initCharts() {
        this.initMessagesChart();
        this.initTokenUsageChart();
    }

    initMessagesChart() {
        const ctx = document.getElementById('messagesChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.messages) {
            this.charts.messages.destroy();
        }

        const data = this.stats.messagesPerDay || this.generateSampleMessagesData();
        
        this.charts.messages = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date),
                datasets: [{
                    label: 'Messages',
                    data: data.map(item => item.count),
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: document.body.classList.contains('dark-mode') ? '#e5e7eb' : '#6b7280'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: document.body.classList.contains('dark-mode') ? '#e5e7eb' : '#6b7280'
                        }
                    }
                }
            }
        });
    }

    initTokenUsageChart() {
        const ctx = document.getElementById('tokenUsageChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.tokenUsage) {
            this.charts.tokenUsage.destroy();
        }

        const data = this.stats.tokenUsageByBot || this.generateSampleTokenData();
        
        // Generate colors for each bot
        const colors = this.generateChartColors(data.length);
        
        this.charts.tokenUsage = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.botName),
                datasets: [{
                    data: data.map(item => item.tokens),
                    backgroundColor: colors,
                    borderColor: document.body.classList.contains('dark-mode') ? '#1a1a2e' : '#ffffff',
                    borderWidth: 2,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: document.body.classList.contains('dark-mode') ? '#e5e7eb' : '#6b7280',
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${this.formatNumber(value)} tokens (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });
    }

    async loadRecentActivity() {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        const activities = this.stats.recentActivity || this.generateSampleActivity();
        
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    ${this.getActivityIcon(activity.type)}
                </div>
                <div class="activity-content">
                    <div class="activity-text">${activity.text}</div>
                    <div class="activity-time">${this.formatTimeAgo(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            'chat': '<i class="fas fa-comment"></i>',
            'bot_created': '<i class="fas fa-robot"></i>',
            'bot_updated': '<i class="fas fa-edit"></i>',
            'bot_deleted': '<i class="fas fa-trash"></i>',
            'github_push': '<i class="fab fa-github"></i>'
        };
        return icons[type] || '<i class="fas fa-circle"></i>';
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        const diffMs = now - past;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
        
        return past.toLocaleDateString();
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    generateChartColors(count) {
        const baseColors = [
            '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
        ];
        
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        return colors;
    }

    generateSampleMessagesData() {
        const dates = [];
        const today = new Date();
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            dates.push({
                date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                count: Math.floor