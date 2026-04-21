// static/js/chat.js
// Chat functionality for Bot Manager application

class ChatManager {
    constructor() {
        this.currentBot = null;
        this.conversation = [];
        this.isTyping = false;
        this.typingIndicator = null;
        this.initializeElements();
        this.bindEvents();
        this.loadFromStorage();
    }

    initializeElements() {
        // Chat UI elements
        this.chatArea = document.getElementById('chatArea');
        this.messageContainer = document.getElementById('messageContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.exportChatBtn = document.getElementById('exportChatBtn');
        this.currentBotName = document.getElementById('currentBotName');
        this.charCount = document.getElementById('charCount');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        // Bot selection
        this.botList = document.getElementById('botList');
    }

    bindEvents() {
        // Message input events
        this.messageInput.addEventListener('input', this.updateCharCount.bind(this));
        this.messageInput.addEventListener('keydown', this.handleKeyDown.bind(this));
        this.sendButton.addEventListener('click', this.sendMessage.bind(this));
        
        // Chat control events
        this.clearChatBtn.addEventListener('click', this.clearChat.bind(this));
        this.exportChatBtn.addEventListener('click', this.exportChat.bind(this));
        
        // Bot selection events (delegated)
        this.botList.addEventListener('click', this.handleBotSelection.bind(this));
        
        // Load previous conversations when bot is selected
        document.addEventListener('botSelected', (e) => {
            this.setCurrentBot(e.detail.bot);
        });
    }

    loadFromStorage() {
        // Load last active bot from localStorage
        const lastBotId = localStorage.getItem('lastActiveBot');
        if (lastBotId) {
            // Bot will be loaded when app initializes
            console.log('Last active bot:', lastBotId);
        }
    }

    setCurrentBot(bot) {
        this.currentBot = bot;
        this.conversation = [];
        
        // Update UI
        this.currentBotName.textContent = bot.name;
        this.messageInput.disabled = false;
        this.sendButton.disabled = false;
        
        // Load conversation history
        this.loadConversationHistory(bot.id);
        
        // Save as last active bot
        localStorage.setItem('lastActiveBot', bot.id);
        
        // Focus input
        setTimeout(() => {
            this.messageInput.focus();
        }, 100);
    }

    async loadConversationHistory(botId) {
        try {
            const response = await fetch(`/api/bots/${botId}/history`);
            if (response.ok) {
                const history = await response.json();
                this.displayConversationHistory(history);
            }
        } catch (error) {
            console.error('Error loading conversation history:', error);
            this.showToast('Error loading conversation history', 'error');
        }
    }

    displayConversationHistory(history) {
        // Clear current messages
        this.messageContainer.innerHTML = '';
        this.conversation = [];
        
        if (history && history.length > 0) {
            // Sort by timestamp
            history.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            
            // Display each message
            history.forEach(msg => {
                this.conversation.push(msg);
                this.appendMessage(msg);
            });
            
            // Scroll to bottom
            this.scrollToBottom();
        } else {
            // Show empty state
            this.showEmptyState();
        }
    }

    updateCharCount() {
        const length = this.messageInput.value.length;
        this.charCount.textContent = `${length}/4000`;
        
        // Update color based on length
        if (length > 3500) {
            this.charCount.style.color = '#ef4444';
        } else if (length > 2500) {
            this.charCount.style.color = '#f59e0b';
        } else {
            this.charCount.style.color = '#6b7280';
        }
    }

    handleKeyDown(e) {
        // Send message on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
        
        // Clear input on Escape
        if (e.key === 'Escape') {
            this.messageInput.value = '';
            this.updateCharCount();
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            this.showToast('Please enter a message', 'warning');
            return;
        }
        
        if (!this.currentBot) {
            this.showToast('Please select a bot first', 'warning');
            return;
        }
        
        if (this.isTyping) {
            this.showToast('Bot is currently typing...', 'warning');
            return;
        }
        
        // Create user message object
        const userMessage = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
            tokens: this.estimateTokens(message)
        };
        
        // Add to conversation and display
        this.conversation.push(userMessage);
        this.appendMessage(userMessage);
        
        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to API
            const startTime = Date.now();
            const response = await this.sendToDeepSeek(userMessage);
            const responseTime = Date.now() - startTime;
            
            // Create bot message object
            const botMessage = {
                role: 'assistant',
                content: response.content,
                timestamp: new Date().toISOString(),
                tokens: response.usage?.completion_tokens || this.estimateTokens(response.content),
                responseTime: responseTime,
                totalTokens: response.usage?.total_tokens || 0
            };
            
            // Add to conversation and display
            this.conversation.push(botMessage);
            this.appendMessage(botMessage);
            
            // Save conversation
            await this.saveConversation();
            
            // Update analytics
            this.updateAnalytics(botMessage);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast(`Error: ${error.message}`, 'error');
            
            // Add error message to conversation
            const errorMessage = {
                role: 'assistant',
                content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
                timestamp: new Date().toISOString(),
                isError: true
            };
            
            this.conversation.push(errorMessage);
            this.appendMessage(errorMessage);
        } finally {
            // Hide typing indicator
            this.hideTypingIndicator();
        }
    }

    async sendToDeepSeek(userMessage) {
        if (!this.currentBot) {
            throw new Error('No bot selected');
        }
        
        // Prepare messages for API
        const messages = [
            {
                role: 'system',
                content: this.currentBot.system_prompt || 'You are a helpful AI assistant.'
            },
            ...this.conversation.map(msg => ({
                role: msg.role,
                content: msg.content
            }))
        ];
        
        // Prepare request body
        const requestBody = {
            model: 'deepseek-chat',
            messages: messages,
            temperature: this.currentBot.temperature || 0.7,
            max_tokens: this.currentBot.max_tokens || 2048,
            stream: false
        };
        
        // Send request with retry logic
        let lastError;
        for (let attempt = 1; attempt <= 3; attempt++) {
            try {
                const response = await fetch(`/api/bots/${this.currentBot.id}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }
                
                const data = await response.json();
                
                // Check for API errors
                if (data.error) {
                    throw new Error(data.error);
                }
                
                return data;
                
            } catch (error) {
                lastError = error;
                
                // Don't retry on certain errors
                if (error.message.includes('401') || error.message.includes('Invalid API key')) {
                    throw error;
                }
                
                // Wait before retry (exponential backoff)
                if (attempt < 3) {
                    await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
                }
            }
        }
        
        throw lastError || new Error('Failed after 3 attempts');
    }

    appendMessage(message) {
        const messageElement = this.createMessageElement(message);
        this.messageContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.role} ${message.isError ? 'error' : ''}`;