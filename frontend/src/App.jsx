import { useState, useEffect, useRef } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { systemService } from './services/api';

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [selectedModel, setSelectedModel] = useState('openai/gpt-4o-mini-2024-07-18');

  useEffect(() => {
    loadSystemStatus();
  }, []);

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
    console.log('Model changed to:', model);
  };

  return (
    <div className="app">
      <Header
        systemStatus={systemStatus}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        isSidebarOpen={isSidebarOpen}
        selectedModel={selectedModel}
        onModelChange={handleModelChange}
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
          selectedModel={selectedModel}
        />
      </div>
    </div>
  );
}

export default App;
