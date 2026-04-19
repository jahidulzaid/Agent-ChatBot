import { useState, useEffect } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { systemService } from './services/api';

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [modelCatalog, setModelCatalog] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openrouter');
  const [selectedModel, setSelectedModel] = useState('openai/gpt-4o-mini-2024-07-18');

  useEffect(() => {
    loadInitialData();
  }, []);

  const getModelsForProvider = (provider, catalog) => {
    if (!catalog?.models_by_provider) return [];
    if (provider === 'auto') {
      const recommended = catalog.recommended_provider || 'openrouter';
      return catalog.models_by_provider[recommended] || [];
    }
    return catalog.models_by_provider[provider] || [];
  };

  const loadInitialData = async () => {
    try {
      const [status, models] = await Promise.all([
        systemService.getStatus(),
        systemService.getModels(),
      ]);
      setSystemStatus(status);
      setModelCatalog(models);

      const initialProvider = models.recommended_provider || 'openrouter';
      const availableModels = getModelsForProvider(initialProvider, models);
      const defaultModel = models.default_models?.[initialProvider];

      setSelectedProvider(initialProvider);
      if (defaultModel && availableModels.some((model) => model.id === defaultModel)) {
        setSelectedModel(defaultModel);
      } else if (availableModels.length > 0) {
        setSelectedModel(availableModels[0].id);
      }
    } catch (error) {
      console.error('Failed to load initial app data:', error);
      loadSystemStatus();
    }
  };

  const loadSystemStatus = async () => {
    try {
      const status = await systemService.getStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const handleNewMessage = (role, content) => {
    setConversationHistory((prev) => [...prev, { role, content }]);
  };

  const handleClearChat = () => {
    setConversationHistory([]);
  };

  const handleModelChange = (model) => {
    setSelectedModel(model);
  };

  const handleProviderChange = (provider) => {
    setSelectedProvider(provider);
    const models = getModelsForProvider(provider, modelCatalog);
    if (!models.some((model) => model.id === selectedModel) && models.length > 0) {
      setSelectedModel(models[0].id);
    }
  };

  return (
    <div className="app">
      <Header
        systemStatus={systemStatus}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        isSidebarOpen={isSidebarOpen}
        selectedModel={selectedModel}
        onModelChange={handleModelChange}
        selectedProvider={selectedProvider}
        onProviderChange={handleProviderChange}
        modelCatalog={modelCatalog}
      />
      
      <div className="app-content">
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          onStatusUpdate={loadSystemStatus}
          onClearChat={handleClearChat}
        />
        
        <ChatInterface
          conversationHistory={conversationHistory}
          onNewMessage={handleNewMessage}
          onClearChat={handleClearChat}
          onOpenUpload={() => setIsSidebarOpen(true)}
          selectedModel={selectedModel}
          selectedProvider={selectedProvider}
        />
      </div>
    </div>
  );
}

export default App;
