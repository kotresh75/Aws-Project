/**
 * Chatbot Widget Component
 * Handles the floating chat interface and API communication
 */

function initChatbot() {
    // Inject HTML
    const chatbotHTML = `
        <div id="chat-widget">
            <button id="chat-toggle-btn">
                <span>💬</span>
            </button>
            <div id="chat-window" class="hidden">
                <div class="chat-header">
                    <h3>🤖 Library Assistant</h3>
                    <button id="chat-close-btn">×</button>
                </div>
                <div id="chat-messages">
                    <div class="message bot">Hello! I'm your AI library assistant. How can I help you today?</div>
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chat-input" placeholder="Ask about books, rules, etc...">
                    <button id="chat-send-btn">
                        <svg viewBox="0 0 24 24"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"></path></svg>
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatbotHTML);

    // Elements
    const widget = document.getElementById('chat-widget');
    const toggleBtn = document.getElementById('chat-toggle-btn');
    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('chat-close-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');

    // State
    let isOpen = false;

    // Functions
    function toggleChat() {
        isOpen = !isOpen;
        if (isOpen) {
            chatWindow.classList.remove('hidden');
            chatWindow.style.display = 'flex';
            input.focus();
        } else {
            chatWindow.classList.add('hidden');
            setTimeout(() => {
                if (!isOpen) chatWindow.style.display = 'none';
            }, 300);
        }
    }

    function addMessage(text, isUser = false) {
        const div = document.createElement('div');
        div.className = `message ${isUser ? 'user' : 'bot'}`;
        div.textContent = text;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showTyping() {
        const id = 'typing-' + Date.now();
        const html = `
            <div class="typing-indicator" id="${id}">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', html);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return id;
    }

    function removeTyping(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // Add user message
        addMessage(text, true);
        input.value = '';

        // Show typing
        const typingId = showTyping();

        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: text }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Remove typing and add bot response
            removeTyping(typingId);
            addMessage(data.response || "I didn't get a response.");
        } catch (error) {
            removeTyping(typingId);
            addMessage("Sorry, I'm having trouble connecting to the server. Please ensure the backend is running.");
            console.error('Chat Error:', error);
        }
    }

    // Event Listeners
    toggleBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    sendBtn.addEventListener('click', sendMessage);

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
} else {
    initChatbot();
}
