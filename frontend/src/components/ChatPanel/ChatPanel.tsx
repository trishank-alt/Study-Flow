import { useState, useEffect, useRef } from 'react';
import { aiService } from '../../services/ai';
import type { ChatHistoryItem } from '../../types';
import './ChatPanel.css';

export default function ChatPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatHistoryItem[]>([
    {
      role: 'assistant',
      content: 'Hello! I am your AI study tutor. I can explain complex topics, review your schedule, or generate quizzes. How can I help you today?',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isSending) return;

    const userMessage: ChatHistoryItem = {
      role: 'user',
      content: inputValue.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsSending(true);

    try {
      // Send chat history to backend
      const history = [...messages, userMessage];
      const data = await aiService.chat(history);
      
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.reply,
        },
      ]);
    } catch (err: unknown) {
      console.error(err);
      const axiosError = err as { response?: { data?: { detail?: string } } };
      const detailMessage = axiosError.response?.data?.detail;
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: detailMessage ? `⚠️ ${detailMessage}` : '⚠️ Failed to connect to the AI tutor. Please check your settings and connection.',
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        className={`chat-toggle-btn ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Chat with AI Tutor"
        id="ai-chat-toggle"
      >
        {isOpen ? '❌' : '🤖'}
      </button>

      {/* Slide-out Chat Panel */}
      <div className={`chat-panel-container ${isOpen ? 'visible' : ''}`}>
        <div className="chat-panel-header">
          <div className="chat-header-title">
            <span className="chat-avatar-icon">🤖</span>
            <div>
              <h4>AI Study Tutor</h4>
              <span className="chat-subtitle">Always here to help</span>
            </div>
          </div>
          <button className="chat-close-btn" onClick={() => setIsOpen(false)}>
            ✕
          </button>
        </div>

        <div className="chat-panel-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message-row ${msg.role}`}>
              <div className="chat-message-bubble">
                {/* Renders basic markdown syntax for paragraphs, lists, and bold text */}
                <div dangerouslySetInnerHTML={{
                  __html: msg.content
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/`([^`]+)`/g, '<code>$1</code>')
                    .replace(/\n/g, '<br />')
                }} />
              </div>
            </div>
          ))}
          {isSending && (
            <div className="chat-message-row assistant">
              <div className="chat-message-bubble loading-bubble">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="chat-panel-input-form">
          <input
            className="chat-panel-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask your study tutor a question..."
            disabled={isSending}
            required
            autoComplete="off"
          />
          <button type="submit" className="chat-send-btn" disabled={isSending || !inputValue.trim()}>
            ➔
          </button>
        </form>
      </div>
    </>
  );
}
