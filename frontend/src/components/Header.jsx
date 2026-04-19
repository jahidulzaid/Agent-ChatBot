import { Menu, X, Activity } from 'lucide-react';
import './Header.css';

function Header({
  systemStatus,
  onToggleSidebar,
  isSidebarOpen,
  selectedModel,
  onModelChange,
  selectedProvider,
  onProviderChange,
  modelCatalog,
}) {
  const providers = modelCatalog?.providers || ['openrouter', 'openai'];
  const effectiveProvider = selectedProvider === 'auto'
    ? modelCatalog?.recommended_provider || 'openrouter'
    : selectedProvider;
  const modelOptions = modelCatalog?.models_by_provider?.[effectiveProvider] || [];

  const formatProviderLabel = (provider) => {
    if (provider === 'openrouter') return 'OpenRouter';
    if (provider === 'openai') return 'OpenAI';
    return 'Auto';
  };

  return (
    <header className="header">
      <div className="header-left">
        <button className="toggle-sidebar-btn" onClick={onToggleSidebar}>
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <h1 className="header-title">Agentic RAG Studio</h1>
      </div>
      
      <div className="header-center">
        <select
          className="provider-selector"
          value={selectedProvider}
          onChange={(e) => onProviderChange(e.target.value)}
          title="Select LLM provider"
        >
          {providers.map((provider) => (
            <option key={provider} value={provider}>
              {formatProviderLabel(provider)}
            </option>
          ))}
        </select>

        <select 
          className="model-selector" 
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          title="Select AI model"
          disabled={modelOptions.length === 0}
        >
          {modelOptions.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} ({model.provider})
            </option>
          ))}
        </select>
      </div>
      
      <div className="header-right">
        {systemStatus && (
          <div className="provider-health">
            <span className={`key-dot ${systemStatus.has_openrouter_key ? 'up' : 'down'}`} title="OpenRouter key" />
            <span className={`key-dot ${systemStatus.has_openai_key ? 'up' : 'down'}`} title="OpenAI key" />
          </div>
        )}
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
