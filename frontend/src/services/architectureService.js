import { apiClient } from './api';
import { extractApiErrorMessage } from '../utils/errorUtils';

class ArchitectureService {
  async generateArchitecture(questionnaireData) {
    try {
      const response = await apiClient.post('/architecture/generate', questionnaireData);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to generate architecture. Please try again.'));
    }
  }

  async getArchitecture(architectureId) {
    try {
      const response = await apiClient.get(`/architecture/${architectureId}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Architecture not found');
      }
      throw new Error(extractApiErrorMessage(error, 'Failed to retrieve architecture. Please try again.'));
    }
  }

  async listArchitectures() {
    try {
      const response = await apiClient.get('/architecture/');
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to list architectures. Please try again.'));
    }
  }

  async healthCheck() {
    try {
      const response = await apiClient.get('/health/');
      return response.data;
    } catch (error) {
      throw new Error('Service is currently unavailable');
    }
  }
}

export const architectureService = new ArchitectureService();