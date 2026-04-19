import { useState } from 'react';
import { Upload, FileText, Trash2, X, Loader } from 'lucide-react';
import { documentService } from '../services/api';
import './Sidebar.css';

function Sidebar({ isOpen, onClose, onStatusUpdate, onClearChat }) {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      const result = await documentService.uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });

      setUploadStatus({
        type: 'success',
        message: result.message,
      });

      onStatusUpdate();
      
      setTimeout(() => {
        setUploadStatus(null);
        setUploadProgress(0);
      }, 3000);
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Upload failed',
      });
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const handleClearDocuments = async () => {
    if (!window.confirm('Are you sure you want to clear all documents?')) return;

    try {
      await documentService.clearDocuments();
      setUploadStatus({
        type: 'success',
        message: 'All documents cleared',
      });
      onStatusUpdate();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: 'Failed to clear documents',
      });
    }
  };

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Document Vault</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-content">
          <div className="upload-section">
            <label className="upload-btn">
              <input
                type="file"
                accept=".pdf,.docx,.txt,.md"
                onChange={handleFileUpload}
                disabled={uploading}
              />
              {uploading ? (
                <>
                  <Loader className="spinner" size={20} />
                  <span>Uploading... {uploadProgress}%</span>
                </>
              ) : (
                <>
                  <Upload size={20} />
                  <span>Upload Document</span>
                </>
              )}
            </label>

            {uploading && (
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}

            {uploadStatus && (
              <div className={`upload-status ${uploadStatus.type}`}>
                {uploadStatus.message}
              </div>
            )}
          </div>

          <div className="supported-formats">
            <h3>Supported Formats</h3>
            <ul>
              <li><FileText size={16} /> PDF (.pdf)</li>
              <li><FileText size={16} /> Word (.docx)</li>
              <li><FileText size={16} /> Text (.txt)</li>
              <li><FileText size={16} /> Markdown (.md)</li>
            </ul>
          </div>

          <div className="actions-section">
            <button className="action-btn danger" onClick={handleClearDocuments}>
              <Trash2 size={18} />
              Clear All Documents
            </button>
            <button className="action-btn" onClick={onClearChat}>
              <Trash2 size={18} />
              Clear Chat History
            </button>
          </div>
        </div>
      </div>
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
    </>
  );
}

export default Sidebar;
