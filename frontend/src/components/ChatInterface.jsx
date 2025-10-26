import { useState, useRef, useEffect } from 'react';
import { Send, Loader, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { chatService } from '../services/api';
import './ChatInterface.css';

function ChatInterface({ conversationHistory, onNewMessage, onClearChat }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (conversationHistory.length === 0) {
      setMessages([]);
    }
  }, [conversationHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);
    onNewMessage('user', userMessage);

    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(userMessage, conversationHistory);

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
        reasoning: response.reasoning_trace,
        iterations: response.iterations,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      onNewMessage('assistant', response.answer);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    const showReasoning = message.reasoning && message.reasoning.length > 0;

    return (
      <div key={index} className={`message ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-avatar">
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>
        <div className="message-content">
          <div className="message-text">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          {showReasoning && (
            <details className="reasoning-trace">
              <summary>🧠 View reasoning process ({message.iterations} iterations)</summary>
              <div className="reasoning-content">
                {message.reasoning.map((step, idx) => (
                  <div key={idx} className={`reasoning-step ${step.type}`}>
                    <div className="step-header">
                      <span className="step-type">{step.type.toUpperCase()}</span>
                      <span className="step-iteration">Iteration {step.iteration}</span>
                    </div>
                    {step.type === 'thought' && (
                      <div className="step-content">{step.content}</div>
                    )}
                    {step.type === 'action' && (
                      <div className="step-content">
                        <strong>Tool:</strong> {step.tool}
                        <br />
                        <strong>Input:</strong> {JSON.stringify(step.input)}
                      </div>
                    )}
                    {step.type === 'observation' && (
                      <div className="step-content">{step.content}</div>
                    )}
                  </div>
                ))}
              </div>
            </details>
          )}
          <div className="message-timestamp">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <Bot size={48} />
            <h2>Welcome to Agentic RAG Chatbot!</h2>
            <p>I can help you with information from uploaded documents and perform various tasks.</p>
            <div className="example-prompts">
              <button onClick={() => setInput('What documents do you have?')}>
                What documents do you have?
              </button>
              <button onClick={() => setInput('Search for information about...')}>
                Search for information
              </button>
              <button onClick={() => setInput('What is the current time?')}>
                What is the current time?
              </button>
            </div>
          </div>
        )}
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          disabled={isLoading}
          className="message-input"
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="send-button"
        >
          {isLoading ? <Loader className="spinner" size={20} /> : <Send size={20} />}
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;
