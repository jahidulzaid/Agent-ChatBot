import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (message, conversationHistory = []) => {
    const response = await api.post('/chat', {
      message,
      conversation_history: conversationHistory,
      use_rag: true,
    });
    return response.data;
  },

  streamMessage: async (message, conversationHistory = []) => {
    const response = await api.post('/chat/stream', {
      message,
      conversation_history: conversationHistory,
    }, {
      responseType: 'stream'
    });
    return response.data;
  },
};

export const documentService = {
  uploadDocument: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  searchDocuments: async (query, topK = 5) => {
    const response = await api.post('/documents/search', {
      query,
      top_k: topK,
    });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/documents/stats');
    return response.data;
  },

  clearDocuments: async () => {
    const response = await api.delete('/documents/clear');
    return response.data;
  },
};

export const systemService = {
  getStatus: async () => {
    const response = await api.get('/status');
    return response.data;
  },

  getTools: async () => {
    const response = await api.get('/tools');
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
