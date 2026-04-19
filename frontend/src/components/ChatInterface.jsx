import { useState, useRef, useEffect } from 'react';
import { Send, Loader, Bot, User, Upload } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { chatService } from '../services/api';
import './ChatInterface.css';

function ChatInterface({ conversationHistory, onNewMessage, onOpenUpload, selectedModel, selectedProvider }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

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

  useEffect(() => {
    if (!textareaRef.current) {
      return;
    }

    textareaRef.current.style.height = 'auto';
    textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
  }, [input]);

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && input.trim()) {
        handleSubmit(e);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    const newUserMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);
    onNewMessage('user', userMessage);

    setIsLoading(true);

    const assistantMessageId = `assistant-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const initialAssistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      reasoning: [],
      iterations: 0,
      isStreaming: true,
    };
    setMessages((prev) => [...prev, initialAssistantMessage]);

    try {
      const response = await chatService.streamMessage(
        userMessage,
        conversationHistory,
        selectedModel,
        selectedProvider,
        true,
        (event) => {
          if (event.event === 'trace' && event.step) {
            const step = event.step;
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) {
                  return msg;
                }

                const nextReasoning = [...(msg.reasoning || []), step];
                const nextIterations = Math.max(msg.iterations || 0, step.iteration || 0);
                const nextContent = step.type === 'answer' ? step.content : msg.content;

                return {
                  ...msg,
                  reasoning: nextReasoning,
                  iterations: nextIterations,
                  content: nextContent,
                };
              })
            );
          }

          if (event.event === 'final' && event.result) {
            const result = event.result;
            setMessages((prev) =>
              prev.map((msg) => {
                if (msg.id !== assistantMessageId) {
                  return msg;
                }

                return {
                  ...msg,
                  content: result.answer || msg.content,
                  reasoning: result.reasoning_trace || msg.reasoning,
                  iterations: result.iterations || msg.iterations,
                  provider: result.provider,
                  model: result.model,
                  isStreaming: false,
                };
              })
            );
          }
        }
      );

      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.id !== assistantMessageId) {
            return msg;
          }

          return {
            ...msg,
            content: response.answer,
            reasoning: response.reasoning_trace,
            iterations: response.iterations,
            provider: response.provider,
            model: response.model,
            isStreaming: false,
          };
        })
      );

      onNewMessage('assistant', response.answer);
    } catch (error) {
      console.error('Chat error:', error);
      const errorDetail = error.message || 'Sorry, I encountered an error. Please check your provider/API key setup and try again.';
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.id !== assistantMessageId) {
            return msg;
          }
          return {
            ...msg,
            content: errorDetail,
            isError: true,
            isStreaming: false,
          };
        })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    const showReasoning = message.reasoning && message.reasoning.length > 0;

    return (
      <div key={message.id || index} className={`message ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-avatar">
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>
        <div className="message-content">
          <div className="message-text">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || (message.isStreaming ? 'Working on your request...' : '')}
            </ReactMarkdown>
          </div>
          {message.provider && message.model && (
            <div className="message-meta">
              {message.provider} • {message.model}
            </div>
          )}
          {showReasoning && (
            <details className="reasoning-trace" open={Boolean(message.isStreaming)}>
              <summary>reasoning trace ({message.iterations} iterations)</summary>
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
                    {step.type === 'answer' && (
                      <div className="step-content">{step.content}</div>
                    )}
                    {step.type === 'system' && (
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
            <h2>Welcome to Agentic RAG Studio</h2>
            <p>Upload documents, query your knowledge base, and switch providers/models for each conversation.</p>
            <div className="example-prompts">
              <button onClick={() => setInput('What documents do you have?')}>
                What documents do you have?
              </button>
              <button onClick={() => setInput('Search for information about...')}>
                Search for information
              </button>
              <button onClick={() => setInput('Compare OpenRouter and OpenAI model responses for this query')}>
                Compare model responses
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
              <div className="message-meta">Agent is thinking and may call tools...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <button
          type="button"
          onClick={onOpenUpload}
          className="attach-button"
          title="Upload documents"
          disabled={isLoading}
        >
          <Upload size={18} />
        </button>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleInputKeyDown}
          placeholder="Ask me anything..."
          disabled={isLoading}
          className="message-input"
          rows={1}
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
