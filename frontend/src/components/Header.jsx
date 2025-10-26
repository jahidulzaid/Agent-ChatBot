import { Menu, X, Activity } from 'lucide-react';
import './Header.css';

function Header({ systemStatus, onToggleSidebar, isSidebarOpen, selectedModel, onModelChange }) {
  const freeModels = [
    { id: 'openai/gpt-4o-mini-2024-07-18', name: 'GPT-4o Mini', provider: 'OpenAI' },
    { id: 'google/gemini-flash-1.5', name: 'Gemini Flash 1.5', provider: 'Google' },
    { id: 'meta-llama/llama-3.2-3b-instruct:free', name: 'Llama 3.2 3B', provider: 'Meta' },
    { id: 'microsoft/phi-3-mini-128k-instruct:free', name: 'Phi-3 Mini', provider: 'Microsoft' },
    { id: 'mistralai/mistral-7b-instruct:free', name: 'Mistral 7B', provider: 'Mistral' },
    { id: 'qwen/qwen-2-7b-instruct:free', name: 'Qwen 2 7B', provider: 'Qwen' }
  ];

  return (
    <header className="header">
      <div className="header-left">
        <button className="toggle-sidebar-btn" onClick={onToggleSidebar}>
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <h1 className="header-title">🤖 Agentic RAG Chatbot</h1>
      </div>
      
      <div className="header-center">
        <select 
          className="model-selector" 
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          title="Select AI Model"
        >
          {freeModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} ({model.provider})
            </option>
          ))}
        </select>
      </div>
      
      <div className="header-right">
        {systemStatus && (
          <div className="status-badge">
            <Activity size={16} />
            <span>{systemStatus.total_documents} docs</span>
          </div>
        )}
        <div className="status-indicator" title="System operational">
          <span className="status-dot"></span>
        </div>
      </div>
    </header>
  );
}

export default Header;
