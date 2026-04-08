// Modern PIXEL Desktop Chat Interface JavaScript

class PixelChatInterface {
    constructor() {
        this.theme = localStorage.getItem('pixelTheme') || 'dark';
        this.isVoiceActive = false;
        this.isTyping = false;
        this.messageHistory = [];
        
        this.init();
    }

    init() {
        this.initTheme();
        this.initEventListeners();
        this.initEelCallbacks();
        this.showWelcomeMessage();
    }

    // Theme Management
    initTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeIcon();
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('pixelTheme', this.theme);
        this.updateThemeIcon();
        this.addSystemMessage(`Switched to ${this.theme} theme`);
    }

    updateThemeIcon() {
        const icon = document.querySelector('#themeToggle i');
        if (icon) {
            icon.className = this.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    // Event Listeners
    initEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Voice button
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
        }

        // Send button
        const sendBtn = document.getElementById('userInputButton');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Input field
        const input = document.getElementById('userInput');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });

            input.addEventListener('input', () => this.handleInputChange());
            input.addEventListener('focus', () => this.showSuggestions());
            input.addEventListener('blur', () => {
                // Delay hiding suggestions to allow clicking
                setTimeout(() => this.hideSuggestions(), 200);
            });
        }

        // Suggestion items
        this.bindSuggestionEvents();

        // Settings button
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }
    }

    bindSuggestionEvents() {
        const suggestions = document.querySelectorAll('.suggestion-item');
        suggestions.forEach(item => {
            item.addEventListener('click', () => {
                const command = item.getAttribute('data-command');
                document.getElementById('userInput').value = command;
                this.hideSuggestions();
                this.sendMessage();
            });
        });
    }

    // Eel Callbacks
    initEelCallbacks() {
        // Expose functions to Python
        if (typeof eel !== 'undefined') {
            eel.expose(this.addUserMsg, 'addUserMsg');
            eel.expose(this.addAppMsg, 'addAppMsg');
        }
    }

    // Message Handling
    sendMessage() {
        const input = document.getElementById('userInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addUserMessage(message);
        
        // Clear input
        input.value = '';
        this.hideSuggestions();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to Python backend
        if (typeof eel !== 'undefined') {
            eel.getUserInput(message);
        }
        
        // Add to history
        this.messageHistory.push({ type: 'user', content: message, timestamp: new Date() });
    }

    addUserMessage(message) {
        const messagesArea = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        
        messageDiv.innerHTML = `
            <div class=\"message-bubble\">
                ${this.formatMessage(message)}
                <div class=\"message-time\">${this.getCurrentTime()}</div>
            </div>
        `;
        
        messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
        this.animateMessage(messageDiv);
    }

    addAssistantMessage(message) {
        this.hideTypingIndicator();
        
        const messagesArea = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        
        messageDiv.innerHTML = `
            <div class=\"message-bubble\">
                ${this.formatMessage(message)}
                <div class=\"message-time\">${this.getCurrentTime()}</div>
            </div>
        `;
        
        messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
        this.animateMessage(messageDiv);
        
        // Add to history
        this.messageHistory.push({ type: 'assistant', content: message, timestamp: new Date() });
    }

    addSystemMessage(message) {
        const messagesArea = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        messageDiv.style.textAlign = 'center';
        messageDiv.style.opacity = '0.7';
        messageDiv.style.fontSize = '0.875rem';
        messageDiv.style.margin = '1rem 0';
        
        messageDiv.innerHTML = `
            <div style=\"background: var(--glass-bg); padding: 0.5rem 1rem; border-radius: 1rem; display: inline-block;\">
                <i class=\"fas fa-info-circle\" style=\"margin-right: 0.5rem;\"></i>
                ${message}
            </div>
        `;
        
        messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const messagesArea = document.getElementById('messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class=\"typing-indicator\">
                <div class=\"typing-dot\"></div>
                <div class=\"typing-dot\"></div>
                <div class=\"typing-dot\"></div>
            </div>
        `;
        
        messagesArea.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
            this.isTyping = false;
        }
    }

    // Voice Input
    toggleVoiceInput() {
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceViz = document.getElementById('voiceViz');
        
        if (!this.isVoiceActive) {
            this.startVoiceInput();
            voiceBtn.classList.add('active');
            voiceViz.style.display = 'block';
            this.addSystemMessage('Voice input activated - speak now');
        } else {
            this.stopVoiceInput();
            voiceBtn.classList.remove('active');
            voiceViz.style.display = 'none';
            this.addSystemMessage('Voice input deactivated');
        }
    }

    startVoiceInput() {
        this.isVoiceActive = true;
        
        // Simulate voice recognition (replace with actual implementation)
        setTimeout(() => {
            if (this.isVoiceActive) {
                this.stopVoiceInput();
                // Simulate recognized speech
                const input = document.getElementById('userInput');
                input.value = 'pixel help';
                this.addSystemMessage('Voice command recognized');
            }
        }, 3000);
    }

    stopVoiceInput() {
        this.isVoiceActive = false;
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceViz = document.getElementById('voiceViz');
        
        voiceBtn.classList.remove('active');
        voiceViz.style.display = 'none';
    }

    // Suggestions
    handleInputChange() {
        const input = document.getElementById('userInput');
        const value = input.value.toLowerCase();
        
        if (value.length > 0) {
            this.showSuggestions();
            this.filterSuggestions(value);
        } else {
            this.hideSuggestions();
        }
    }

    showSuggestions() {
        const suggestions = document.getElementById('suggestions');
        if (suggestions) {
            suggestions.style.display = 'block';
        }
    }

    hideSuggestions() {
        const suggestions = document.getElementById('suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }

    filterSuggestions(query) {
        const suggestions = document.querySelectorAll('.suggestion-item');
        suggestions.forEach(item => {
            const command = item.getAttribute('data-command').toLowerCase();
            const text = item.textContent.toLowerCase();
            
            if (command.includes(query) || text.includes(query)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Utility Functions
    formatMessage(message) {
        // Basic message formatting
        return message
            .replace(/\\n/g, '<br>')
            .replace(/\\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
            .replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    scrollToBottom() {
        const messagesArea = document.getElementById('messages');
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    animateMessage(messageElement) {
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });
    }

    showWelcomeMessage() {
        // Remove welcome message if it exists and add first system message
        setTimeout(() => {
            this.addSystemMessage('PIXEL Assistant is ready for voice and gesture commands');
        }, 1000);
    }

    showSettings() {
        // Create a simple settings modal
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.innerHTML = `
            <div class=\"modal-overlay\" onclick=\"this.parentElement.remove()\">
                <div class=\"modal-content\" onclick=\"event.stopPropagation()\">
                    <div class=\"modal-header\">
                        <h3><i class=\"fas fa-cog\"></i> Settings</h3>
                        <button class=\"close-btn\" onclick=\"this.closest('.settings-modal').remove()\">
                            <i class=\"fas fa-times\"></i>
                        </button>
                    </div>
                    <div class=\"modal-body\">
                        <div class=\"setting-group\">
                            <label>Theme</label>
                            <select id=\"themeSelect\">
                                <option value=\"dark\" ${this.theme === 'dark' ? 'selected' : ''}>Dark</option>
                                <option value=\"light\" ${this.theme === 'light' ? 'selected' : ''}>Light</option>
                            </select>
                        </div>
                        <div class=\"setting-group\">
                            <label>Voice Sensitivity</label>
                            <input type=\"range\" min=\"1\" max=\"10\" value=\"5\" class=\"slider\">
                        </div>
                        <div class=\"setting-group\">
                            <label>Auto-scroll</label>
                            <input type=\"checkbox\" checked>
                        </div>
                    </div>
                    <div class=\"modal-footer\">
                        <button class=\"btn-secondary\" onclick=\"this.closest('.settings-modal').remove()\">Cancel</button>
                        <button class=\"btn-primary\" onclick=\"pixelChat.saveSettings(this)\">Save</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    saveSettings(button) {
        const modal = button.closest('.settings-modal');
        const themeSelect = modal.querySelector('#themeSelect');
        
        if (themeSelect.value !== this.theme) {
            this.theme = themeSelect.value;
            this.initTheme();
        }
        
        modal.remove();
        this.addSystemMessage('Settings saved successfully');
    }

    // Eel exposed functions
    addUserMsg(message) {
        this.addUserMessage(message);
    }

    addAppMsg(message) {
        this.addAssistantMessage(message);
    }

    // Quick command function
    sendQuickCommand(command) {
        document.getElementById('userInput').value = command;
        this.sendMessage();
    }
}

// Global functions for quick commands
function sendQuickCommand(command) {
    if (window.pixelChat) {
        window.pixelChat.sendQuickCommand(command);
    }
}

// Initialize the chat interface
document.addEventListener('DOMContentLoaded', () => {
    window.pixelChat = new PixelChatInterface();
});

// Add CSS for settings modal
const modalStyles = `
.settings-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1000;
}

.modal-overlay {
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    background: var(--bg-primary);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    width: 90%;
    max-width: 400px;
    box-shadow: var(--glass-shadow);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
    margin: 0;
    color: var(--text-primary);
}

.close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: var(--spacing-sm);
    border-radius: var(--radius-md);
}

.close-btn:hover {
    background: var(--glass-bg);
    color: var(--text-primary);
}

.modal-body {
    padding: var(--spacing-lg);
}

.setting-group {
    margin-bottom: var(--spacing-lg);
}

.setting-group label {
    display: block;
    margin-bottom: var(--spacing-sm);
    color: var(--text-primary);
    font-weight: 500;
}

.setting-group select,
.setting-group input[type=\"range\"] {
    width: 100%;
    padding: var(--spacing-sm);
    background: var(--bg-secondary);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
}

.modal-footer {
    display: flex;
    gap: var(--spacing-sm);
    padding: var(--spacing-lg);
    border-top: 1px solid var(--glass-border);
    justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 500;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-secondary {
    background: var(--glass-bg);
    color: var(--text-primary);
    border: 1px solid var(--glass-border);
}

.btn-primary:hover {
    background: var(--primary-dark);
}

.btn-secondary:hover {
    background: var(--bg-secondary);
}
`;

// Inject modal styles
const styleSheet = document.createElement('style');
styleSheet.textContent = modalStyles;
document.head.appendChild(styleSheet);