import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (message, conversationHistory = [], model = null, provider = null) => {
    const payload = {
      message,
      conversation_history: conversationHistory,
      use_rag: true,
    };
    
    if (model) {
      payload.model = model;
    }

    if (provider) {
      payload.provider = provider;
    }
    
    const response = await api.post('/chat', payload);
    return response.data;
  },

  streamMessage: async (
    message,
    conversationHistory = [],
    model = null,
    provider = null,
    useRag = true,
    onEvent = null
  ) => {
    const payload = {
      message,
      conversation_history: conversationHistory,
      use_rag: useRag,
    };
    
    if (model) {
      payload.model = model;
    }

    if (provider) {
      payload.provider = provider;
    }
    
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let detail = `Streaming request failed with status ${response.status}`;
      try {
        const errJson = await response.json();
        detail = errJson?.detail || detail;
      } catch (error) {
        // Keep fallback detail.
      }
      throw new Error(detail);
    }

    if (!response.body) {
      throw new Error('No response body from streaming endpoint.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let finalResult = null;

    let doneReading = false;
    while (!doneReading) {
      const { value, done } = await reader.read();
      if (done) {
        doneReading = true;
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line) {
          continue;
        }

        try {
          const event = JSON.parse(line);
          if (onEvent) {
            onEvent(event);
          }
          if (event.event === 'final') {
            finalResult = event.result;
          }
        } catch (error) {
          console.warn('Failed to parse stream event:', line, error);
        }
      }
    }

    if (!finalResult) {
      throw new Error('Stream ended without a final result event.');
    }

    return finalResult;
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

  getModels: async () => {
    const response = await api.get('/models');
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
