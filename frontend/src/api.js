/**
 * API client for backend communication.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

class ApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
    });
  }

  setAuthToken(token) {
    if (token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.client.defaults.headers.common['Authorization'];
    }
  }

  async sendMessage(message, conversationHistory = []) {
    const response = await this.client.post('/api/chat-simple', {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  }

  async exportFigmaAsset(nodeName, nodeId, color) {
    const response = await this.client.post('/api/export/figma', {
      node_name: nodeName,
      node_id: nodeId,
      color: color,
    });
    return response.data;
  }

  async sendMessageStreaming(message, conversationHistory = []) {
    const response = await this.client.post(
      '/api/chat',
      {
        message,
        conversation_history: conversationHistory,
      },
      {
        responseType: 'stream',
      }
    );
    return response.data;
  }

  async analyzeImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async syncFigma(force = false) {
    const response = await this.client.post('/api/sync/figma', { force });
    return response.data;
  }

  async syncSlides(force = false) {
    const response = await this.client.post('/api/sync/slides', { force });
    return response.data;
  }

  async getStats() {
    const response = await this.client.get('/api/stats');
    return response.data;
  }

  async healthCheck() {
    const response = await this.client.get('/api/health');
    return response.data;
  }
}

const apiClient = new ApiClient();
export { apiClient };
export default apiClient;

