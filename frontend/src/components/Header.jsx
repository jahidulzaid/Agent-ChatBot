import { Menu, X, Activity } from 'lucide-react';
import './Header.css';

function Header({ systemStatus, onToggleSidebar, isSidebarOpen }) {
  return (
    <header className="header">
      <div className="header-left">
        <button className="toggle-sidebar-btn" onClick={onToggleSidebar}>
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <h1 className="header-title">🤖 Agentic RAG Chatbot</h1>
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
