/**
 * The Intersect Chatbot SDK
 * Easy integration library for Brenda's portfolio chatbot
 * 
 * Usage:
 * const intersect = new IntersectSDK('http://localhost:8000');
 * const response = await intersect.chat('Tell me about Brenda');
 */

class IntersectSDK {
    constructor(apiUrl, options = {}) {
        this.apiUrl = apiUrl.replace(/\/$/, ''); // Remove trailing slash
        this.apiKey = options.apiKey || null;
        this.conversationId = options.conversationId || null;
        this.timeout = options.timeout || 30000; // 30 second default timeout
        
        // Event callbacks
        this.onTypingStart = options.onTypingStart || null;
        this.onTypingEnd = options.onTypingEnd || null;
        this.onError = options.onError || null;
        this.onResponse = options.onResponse || null;
    }
    
    /**
     * Check if the API is healthy and available
     */
    async checkHealth() {
        try {
            const response = await this._fetch('/api/v1/health');
            return {
                success: true,
                data: response,
                status: 'healthy'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                status: 'unhealthy'
            };
        }
    }
    
    /**
     * Send a message to The Intersect
     */
    async chat(message, options = {}) {
        if (!message || typeof message !== 'string' || message.trim().length === 0) {
            throw new Error('Message is required and must be a non-empty string');
        }
        
        if (message.length > 500) {
            throw new Error('Message must be 500 characters or less');
        }
        
        const conversationId = options.conversationId || this.conversationId;
        
        // Trigger typing start callback
        if (this.onTypingStart) {
            this.onTypingStart();
        }
        
        try {
            const requestBody = {
                message: message.trim()
            };
            
            if (conversationId) {
                requestBody.conversation_id = conversationId;
            }
            
            const response = await this._fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
                },
                body: JSON.stringify(requestBody)
            });
            
            // Store conversation ID for future requests
            this.conversationId = response.conversation_id;
            
            const result = {
                success: true,
                response: response.response,
                conversationId: response.conversation_id,
                timestamp: response.timestamp,
                processingTime: response.processing_time
            };
            
            // Trigger response callback
            if (this.onResponse) {
                this.onResponse(result);
            }
            
            return result;
            
        } catch (error) {
            const errorResult = {
                success: false,
                error: error.message,
                timestamp: Date.now() / 1000
            };
            
            // Trigger error callback
            if (this.onError) {
                this.onError(errorResult);
            }
            
            throw error;
        } finally {
            // Trigger typing end callback
            if (this.onTypingEnd) {
                this.onTypingEnd();
            }
        }
    }
    
    /**
     * Clear conversation history
     */
    async clearConversation(conversationId = null) {
        const id = conversationId || this.conversationId;
        
        if (!id) {
            throw new Error('No conversation ID available to clear');
        }
        
        try {
            await this._fetch(`/api/v1/chat/${id}`, {
                method: 'DELETE'
            });
            
            // Clear local conversation ID if it was the one we cleared
            if (id === this.conversationId) {
                this.conversationId = null;
            }
            
            return { success: true, message: 'Conversation cleared' };
        } catch (error) {
            throw error;
        }
    }
    
    /**
     * Get API usage statistics
     */
    async getStats() {
        try {
            const response = await this._fetch('/api/v1/stats');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            throw error;
        }
    }
    
    /**
     * Set conversation ID for maintaining context
     */
    setConversationId(conversationId) {
        this.conversationId = conversationId;
    }
    
    /**
     * Get current conversation ID
     */
    getConversationId() {
        return this.conversationId;
    }
    
    /**
     * Set API key for authentication
     */
    setApiKey(apiKey) {
        this.apiKey = apiKey;
    }
    
    /**
     * Internal fetch wrapper with error handling
     */
    async _fetch(endpoint, options = {}) {
        const url = `${this.apiUrl}${endpoint}`;
        
        const fetchOptions = {
            timeout: this.timeout,
            ...options
        };
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...fetchOptions,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}`;
                
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    // Use default error message if JSON parsing fails
                }
                
                throw new Error(errorMessage);
            }
            
            return await response.json();
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
}

/**
 * Simple Chat Widget for easy website integration
 */
class IntersectChatWidget {
    constructor(apiUrl, containerId, options = {}) {
        this.sdk = new IntersectSDK(apiUrl, options);
        this.container = document.getElementById(containerId);
        this.options = {
            title: options.title || 'The Intersect',
            subtitle: options.subtitle || "Brenda's AI Knowledge Database",
            placeholder: options.placeholder || 'Ask me about Brenda...',
            theme: options.theme || 'default',
            ...options
        };
        
        this.isTyping = false;
        this.render();
        this.init();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="intersect-widget">
                <div class="intersect-header">
                    <h3>${this.options.title}</h3>
                    <p>${this.options.subtitle}</p>
                </div>
                <div class="intersect-messages" id="intersect-messages"></div>
                <div class="intersect-input">
                    <input type="text" id="intersect-input" placeholder="${this.options.placeholder}">
                    <button id="intersect-send">Send</button>
                </div>
            </div>
        `;
        
        // Add CSS if not already present
        if (!document.getElementById('intersect-widget-styles')) {
            const style = document.createElement('style');
            style.id = 'intersect-widget-styles';
            style.textContent = this.getWidgetCSS();
            document.head.appendChild(style);
        }
    }
    
    getWidgetCSS() {
        return `
            .intersect-widget {
                border: 1px solid #ddd;
                border-radius: 10px;
                max-width: 400px;
                background: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .intersect-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 10px 10px 0 0;
            }
            
            .intersect-header h3 {
                margin: 0 0 5px 0;
                font-size: 1.1em;
            }
            
            .intersect-header p {
                margin: 0;
                font-size: 0.9em;
                opacity: 0.9;
            }
            
            .intersect-messages {
                height: 300px;
                overflow-y: auto;
                padding: 15px;
                background: #f8f9fa;
            }
            
            .intersect-message {
                margin-bottom: 10px;
                padding: 8px 12px;
                border-radius: 15px;
                max-width: 80%;
            }
            
            .intersect-message.user {
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            
            .intersect-message.bot {
                background: white;
                border: 1px solid #e9ecef;
            }
            
            .intersect-input {
                display: flex;
                padding: 15px;
                gap: 10px;
                border-top: 1px solid #e9ecef;
            }
            
            .intersect-input input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 20px;
                outline: none;
            }
            
            .intersect-input button {
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 20px;
                cursor: pointer;
            }
            
            .intersect-input button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
        `;
    }
    
    async init() {
        const input = document.getElementById('intersect-input');
        const button = document.getElementById('intersect-send');
        
        // Check health
        const health = await this.sdk.checkHealth();
        if (!health.success) {
            this.addMessage('Sorry, I\'m currently unavailable. Please try again later.', 'bot');
            return;
        }
        
        // Add welcome message
        this.addMessage('Hi! Ask me anything about Brenda\'s background, skills, or services! 😊', 'bot');
        
        // Event listeners
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isTyping) {
                this.sendMessage();
            }
        });
        
        button.addEventListener('click', () => {
            if (!this.isTyping) {
                this.sendMessage();
            }
        });
    }
    
    async sendMessage() {
        const input = document.getElementById('intersect-input');
        const button = document.getElementById('intersect-send');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        input.value = '';
        
        // Show typing
        this.isTyping = true;
        button.disabled = true;
        button.textContent = 'Thinking...';
        
        try {
            const response = await this.sdk.chat(message);
            this.addMessage(response.response, 'bot');
        } catch (error) {
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        } finally {
            this.isTyping = false;
            button.disabled = false;
            button.textContent = 'Send';
        }
    }
    
    addMessage(content, sender) {
        const messagesDiv = document.getElementById('intersect-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `intersect-message ${sender}`;
        messageDiv.textContent = content;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { IntersectSDK, IntersectChatWidget };
}

// Make available globally
if (typeof window !== 'undefined') {
    window.IntersectSDK = IntersectSDK;
    window.IntersectChatWidget = IntersectChatWidget;
}
