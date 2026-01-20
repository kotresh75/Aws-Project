import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { text: "Hello! I'm your AI library assistant. How can I help you today?", isUser: false }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    const toggleChat = () => {
        setIsOpen(!isOpen);
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        // Add user message
        const userMessage = inputValue.trim();
        setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
        setInputValue('');
        setIsTyping(true);

        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            setIsTyping(false);
            setMessages(prev => [...prev, {
                text: data.response || "I didn't get a response.",
                isUser: false
            }]);
        } catch (error) {
            console.error('Chat Error:', error);
            setIsTyping(false);
            setMessages(prev => [...prev, {
                text: "Sorry, I'm having trouble connecting to the server. Please ensure the backend is running.",
                isUser: false
            }]);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div className="chat-widget">
            <button className="chat-toggle-btn" onClick={toggleChat}>
                <span>💬</span>
            </button>

            <div className={`chat-window ${!isOpen ? 'hidden' : ''}`}>
                <div className="chat-header">
                    <h3>🤖 Library Assistant</h3>
                    <button className="chat-close-btn" onClick={toggleChat}>×</button>
                </div>

                <div className="chat-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.isUser ? 'user' : 'bot'}`}>
                            {msg.text}
                        </div>
                    ))}

                    {isTyping && (
                        <div className="typing-indicator">
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                            <div className="typing-dot"></div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Ask about books, rules, etc..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        ref={inputRef}
                    />
                    <button className="chat-send-btn" onClick={handleSendMessage}>
                        <svg viewBox="0 0 24 24"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"></path></svg>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Chatbot;
