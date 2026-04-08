// Modern PIXEL Control System JavaScript

class PixelControlSystem {
    constructor() {
        this.isGestureActive = false;
        this.isVoiceActive = false;
        this.theme = localStorage.getItem('theme') || 'dark';
        this.settings = this.loadSettings();
        
        this.init();
    }

    init() {
        this.initTheme();
        this.initEventListeners();
        this.initStatusUpdates();
        this.loadCommands();
        this.initAnimations();
    }

    // Theme Management
    initTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeIcon();
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateThemeIcon();
        this.showNotification(`Switched to ${this.theme} theme`, 'info');
    }

    updateThemeIcon() {
        const icon = document.querySelector('#themeToggle .theme-icon');
        if (icon) {
            icon.className = this.theme === 'dark' ? 'fas fa-sun theme-icon' : 'fas fa-moon theme-icon';
        }
    }

    // Event Listeners
    initEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Control buttons
        this.bindControlButtons();
        
        // Command input
        this.bindCommandInput();
        
        // Settings
        this.bindSettings();
        
        // Activity feed
        this.bindActivityFeed();
    }

    // Prevent double-clicking buttons
    function preventDoubleClick(button) {
        if (button.disabled) return false;
        button.disabled = true;
        setTimeout(() => {
            button.disabled = false;
        }, 1000);
        return true;
    }

    bindControlButtons() {
        const startGesture = document.getElementById('startGesture');
        const stopGesture = document.getElementById('stopGesture');
        const startVoice = document.getElementById('startVoice');
        const stopVoice = document.getElementById('stopVoice');

        if (startGesture) {
            startGesture.addEventListener('click', (e) => {
                if (this.preventDoubleClick(e.target)) {
                    this.startGestureControl();
                }
            });
        }
        if (stopGesture) {
            stopGesture.addEventListener('click', (e) => {
                if (this.preventDoubleClick(e.target)) {
                    this.stopGestureControl();
                }
            });
        }
        if (startVoice) {
            startVoice.addEventListener('click', (e) => {
                if (this.preventDoubleClick(e.target)) {
                    this.startVoiceControl();
                }
            });
        }
        if (stopVoice) {
            stopVoice.addEventListener('click', (e) => {
                if (this.preventDoubleClick(e.target)) {
                    this.stopVoiceControl();
                }
            });
        }
    }

    preventDoubleClick(button) {
        if (button.disabled) return false;
        button.disabled = true;
        setTimeout(() => {
            button.disabled = false;
        }, 1000);
        return true;
    }

    bindCommandInput() {
        const voiceInput = document.getElementById('voiceInput');
        const sendCommand = document.getElementById('sendVoiceCommand');
        const showCommands = document.getElementById('showCommands');

        if (voiceInput) {
            voiceInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendVoiceCommand();
                }
            });
        }

        if (sendCommand) {
            sendCommand.addEventListener('click', () => this.sendVoiceCommand());
        }

        if (showCommands) {
            showCommands.addEventListener('click', () => this.toggleCommands());
        }
    }

    bindSettings() {
        const saveSettings = document.getElementById('saveSettings');
        if (saveSettings) {
            saveSettings.addEventListener('click', () => this.saveSettings());
        }
    }

    bindActivityFeed() {
        const clearActivity = document.getElementById('clearActivity');
        if (clearActivity) {
            clearActivity.addEventListener('click', () => this.clearActivityFeed());
        }
    }

    // Control Functions
    async startGestureControl() {
        try {
            this.showLoading('startGesture');
            const response = await fetch('/start_gesture', { method: 'POST' });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isGestureActive = true;
                this.updateGestureStatus(true);
                this.showGestureVisualization();
                this.addActivity('Gesture control started', 'success');
            } else {
                this.addActivity(data.message, 'error');
            }
        } catch (error) {
            this.addActivity('Failed to start gesture control', 'error');
        } finally {
            this.hideLoading('startGesture');
        }
    }

    async stopGestureControl() {
        try {
            const response = await fetch('/stop_gesture', { method: 'POST' });
            const data = await response.json();
            
            this.isGestureActive = false;
            this.updateGestureStatus(false);
            this.hideGestureVisualization();
            this.addActivity('Gesture control stopped', 'info');
        } catch (error) {
            this.addActivity('Failed to stop gesture control', 'error');
        }
    }

    async startVoiceControl() {
        try {
            this.showLoading('startVoice');
            const response = await fetch('/start_voice', { method: 'POST' });
            const data = await response.json();
            
            if (data.status === 'success') {
                this.isVoiceActive = true;
                this.updateVoiceStatus(true);
                this.showVoiceWaveform();
                this.addActivity('Voice control started', 'success');
            } else {
                this.addActivity(data.message, 'error');
            }
        } catch (error) {
            this.addActivity('Failed to start voice control', 'error');
        } finally {
            this.hideLoading('startVoice');
        }
    }

    async stopVoiceControl() {
        try {
            const response = await fetch('/stop_voice', { method: 'POST' });
            const data = await response.json();
            
            this.isVoiceActive = false;
            this.updateVoiceStatus(false);
            this.hideVoiceWaveform();
            this.addActivity('Voice control stopped', 'info');
        } catch (error) {
            this.addActivity('Failed to stop voice control', 'error');
        }
    }

    async sendVoiceCommand() {
        const input = document.getElementById('voiceInput');
        const command = input.value.trim();
        
        if (!command) return;

        try {
            const response = await fetch('/process_voice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });
            
            const data = await response.json();
            this.addActivity(`Command: ${command}`, data.status);
            input.value = '';
            
            // Add command to recent commands
            this.addRecentCommand(command);
        } catch (error) {
            this.addActivity('Failed to process command', 'error');
        }
    }

    // Status Updates
    updateGestureStatus(active) {
        const status = document.getElementById('gestureStatus');
        if (status) {
            const dot = status.querySelector('.status-dot');
            const text = status.querySelector('.status-text');
            
            if (dot) {
                dot.className = active ? 'status-dot active' : 'status-dot inactive';
            }
            if (text) {
                text.textContent = active ? 'Active' : 'Inactive';
            }
        }
    }

    updateVoiceStatus(active) {
        const status = document.getElementById('voiceStatus');
        if (status) {
            const dot = status.querySelector('.status-dot');
            const text = status.querySelector('.status-text');
            
            if (dot) {
                dot.className = active ? 'status-dot active' : 'status-dot inactive';
            }
            if (text) {
                text.textContent = active ? 'Active' : 'Inactive';
            }
        }
    }

    updateSystemStatus() {
        const systemStatus = document.getElementById('systemStatus');
        const statusBadge = document.getElementById('systemStatusBadge');
        
        if (systemStatus) {
            const isActive = this.isGestureActive || this.isVoiceActive;
            systemStatus.className = isActive ? 'status-dot active' : 'status-dot inactive';
        }
        
        if (statusBadge) {
            if (this.isGestureActive && this.isVoiceActive) {
                statusBadge.textContent = 'Full Control';
                statusBadge.className = 'status-badge';
            } else if (this.isGestureActive || this.isVoiceActive) {
                statusBadge.textContent = 'Partial Control';
                statusBadge.className = 'status-badge';
            } else {
                statusBadge.textContent = 'Ready';
                statusBadge.className = 'status-badge';
            }
        }
    }

    // Visualizations
    showGestureVisualization() {
        const viz = document.getElementById('gestureViz');
        if (viz) {
            viz.style.display = 'block';
            this.initGestureCanvas();
        }
    }

    hideGestureVisualization() {
        const viz = document.getElementById('gestureViz');
        if (viz) {
            viz.style.display = 'none';
        }
    }

    showVoiceWaveform() {
        const waveform = document.getElementById('voiceWaveform');
        if (waveform) {
            waveform.style.display = 'flex';
        }
    }

    hideVoiceWaveform() {
        const waveform = document.getElementById('voiceWaveform');
        if (waveform) {
            waveform.style.display = 'none';
        }
    }

    initGestureCanvas() {
        const canvas = document.getElementById('gestureCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        let frame = 0;
        
        const animate = () => {
            if (!this.isGestureActive) return;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw hand outline
            ctx.strokeStyle = '#6366f1';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(100, 75, 30 + Math.sin(frame * 0.1) * 5, 0, Math.PI * 2);
            ctx.stroke();
            
            frame++;
            requestAnimationFrame(animate);
        };
        
        animate();
    }

    // Commands Management
    async loadCommands() {
        try {
            const response = await fetch('/get_commands');
            const data = await response.json();
            this.displayCommands(data.commands || []);
        } catch (error) {
            console.error('Failed to load commands:', error);
        }
    }

    displayCommands(commands) {
        const container = document.getElementById('commandsContainer');
        if (!container) return;
        
        if (commands.length === 0) {
            container.innerHTML = '<p class="text-muted">No commands available</p>';
            return;
        }
        
        const commandsHtml = commands.map(cmd => 
            `<span class="command-tag">${cmd}</span>`
        ).join('');
        
        container.innerHTML = commandsHtml;
    }

    toggleCommands() {
        const commandsList = document.getElementById('commandsList');
        const button = document.getElementById('showCommands');
        
        if (commandsList && button) {
            const isVisible = commandsList.style.display !== 'none';
            commandsList.style.display = isVisible ? 'none' : 'block';
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = isVisible ? 'fas fa-list me-1' : 'fas fa-eye-slash me-1';
            }
        }
    }

    // Activity Feed
    addActivity(message, type = 'info') {
        const feed = document.getElementById('statusMessages');
        if (!feed) return;
        
        const activity = document.createElement('div');
        activity.className = `activity-item ${type}`;
        activity.innerHTML = `
            <div class="activity-icon">
                <i class="fas fa-${this.getActivityIcon(type)}"></i>
            </div>
            <div class="activity-content">
                <span class="activity-message">${message}</span>
                <span class="activity-time">${new Date().toLocaleTimeString()}</span>
            </div>
        `;
        
        feed.insertBefore(activity, feed.firstChild);
        
        // Limit to 10 items
        while (feed.children.length > 10) {
            feed.removeChild(feed.lastChild);
        }
        
        // Auto-remove after 5 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                if (activity.parentNode) {
                    activity.remove();
                }
            }, 5000);
        }
    }

    getActivityIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    clearActivityFeed() {
        const feed = document.getElementById('statusMessages');
        if (feed) {
            feed.innerHTML = '';
        }
    }

    // Settings
    loadSettings() {
        const defaultSettings = {
            theme: 'dark',
            animations: true,
            voiceSensitivity: 5,
            wakeWord: 'pixel',
            gestureSmoothing: 7,
            handDetection: 'single'
        };
        
        const saved = localStorage.getItem('pixelSettings');
        return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
    }

    saveSettings() {
        const settings = {
            theme: document.getElementById('themeSelect')?.value || this.theme,
            animations: document.getElementById('animationsToggle')?.checked || true,
            voiceSensitivity: document.getElementById('voiceSensitivity')?.value || 5,
            wakeWord: document.getElementById('wakeWord')?.value || 'pixel',
            gestureSmoothing: document.getElementById('gestureSmoothing')?.value || 7,
            handDetection: document.getElementById('handDetection')?.value || 'single'
        };
        
        localStorage.setItem('pixelSettings', JSON.stringify(settings));
        this.settings = settings;
        
        // Apply theme change
        if (settings.theme !== this.theme) {
            this.theme = settings.theme;
            this.initTheme();
        }
        
        this.showNotification('Settings saved successfully', 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        if (modal) modal.hide();
    }

    // Utilities
    showLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-spinner fa-spin me-2';
            }
        }
    }

    hideLoading(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = buttonId.includes('start') ? 'fas fa-play me-2' : 'fas fa-stop me-2';
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getActivityIcon(type)} me-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    initAnimations() {
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    initStatusUpdates() {
        // Update system status every second
        setInterval(() => {
            this.updateSystemStatus();
        }, 1000);
    }

    addRecentCommand(command) {
        let recent = JSON.parse(localStorage.getItem('recentCommands') || '[]');
        recent = [command, ...recent.filter(c => c !== command)].slice(0, 5);
        localStorage.setItem('recentCommands', JSON.stringify(recent));
    }
}

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pixelSystem = new PixelControlSystem();
});

// Add CSS for toast notifications
const toastStyles = `
.toast-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-md) var(--spacing-lg);
    color: var(--text-primary);
    z-index: 1000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    box-shadow: var(--glass-shadow);
}

.toast-notification.show {
    transform: translateX(0);
}

.toast-notification.success { border-left: 4px solid var(--success); }
.toast-notification.error { border-left: 4px solid var(--danger); }
.toast-notification.warning { border-left: 4px solid var(--warning); }
.toast-notification.info { border-left: 4px solid var(--info); }

.activity-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    margin-bottom: var(--spacing-sm);
    border-left: 3px solid var(--info);
}

.activity-item.success { border-left-color: var(--success); }
.activity-item.error { border-left-color: var(--danger); }
.activity-item.warning { border-left-color: var(--warning); }

.activity-icon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--primary);
    color: white;
    font-size: 0.875rem;
}

.activity-content {
    flex: 1;
}

.activity-message {
    display: block;
    font-weight: 500;
    margin-bottom: var(--spacing-xs);
}

.activity-time {
    font-size: 0.75rem;
    color: var(--text-muted);
}
`;

// Inject toast styles
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);