import axios from 'axios';

const API_BASE_URL = '/api/v1/aws-accounts';

class AWSAccountService {
  async createAccount(accountData) {
    try {
      const response = await axios.post(API_BASE_URL, accountData);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async listAccounts() {
    try {
      const response = await axios.get(API_BASE_URL);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async getAccount(accountId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/${accountId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async updateAccount(accountId, updateData) {
    try {
      const response = await axios.put(`${API_BASE_URL}/${accountId}`, updateData);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async deleteAccount(accountId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/${accountId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async validateAccount(accountId) {
    try {
      const response = await axios.post(`${API_BASE_URL}/${accountId}/validate`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async deployInfrastructure(deploymentData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/deploy`, deploymentData);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async getDeploymentStatus(deploymentId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/deployments/${deploymentId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async destroyInfrastructure(destroyData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/destroy`, destroyData);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async listProjectDeployments(projectId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/deployments/project/${projectId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async getProjectDeploymentStatus(projectId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/deployment-status/project/${projectId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  _handleError(error) {
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.detail || error.response.statusText;
      return new Error(message);
    } else if (error.request) {
      // Network error
      return new Error('Network error - please check your connection');
    } else {
      // Other error
      return new Error(error.message || 'An unexpected error occurred');
    }
  }
}

export const awsAccountService = new AWSAccountService();