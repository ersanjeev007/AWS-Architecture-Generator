import { apiClient } from './api';
import { extractApiErrorMessage } from '../utils/errorUtils';

class ProjectService {
  // Generate architecture and create project in one call
  async generateArchitecture(questionnaireData) {
    try {
      const response = await apiClient.post('/projects/generate-architecture', questionnaireData);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to generate architecture. Please try again.'));
    }
  }

  async createProject(projectData) {
    try {
      const response = await apiClient.post('/projects/', projectData);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to create project. Please try again.'));
    }
  }

  async getProject(projectId) {
    try {
      const response = await apiClient.get(`/projects/${projectId}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Project not found');
      }
      throw new Error(extractApiErrorMessage(error, 'Failed to retrieve project. Please try again.'));
    }
  }

  async listProjects(skip = 0, limit = 100) {
    try {
      const response = await apiClient.get('/projects/', {
        params: { skip, limit }
      });
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to list projects. Please try again.'));
    }
  }

  async updateProject(projectId, projectData) {
    try {
      const response = await apiClient.put(`/projects/${projectId}`, projectData);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to update project. Please try again.'));
    }
  }

  async deleteProject(projectId) {
    try {
      const response = await apiClient.delete(`/projects/${projectId}`);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to delete project. Please try again.'));
    }
  }

  async regenerateArchitecture(projectId) {
    try {
      const response = await apiClient.put(`/projects/${projectId}/regenerate-architecture`);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to regenerate architecture. Please try again.'));
    }
  }

  async getProjectArchitecture(projectId) {
    try {
      const response = await apiClient.get(`/projects/${projectId}/architecture`);
      return response.data;
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Failed to get project architecture. Please try again.'));
    }
  }
}

export const projectService = new ProjectService();