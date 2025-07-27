import axios from 'axios';
import { extractApiErrorMessage } from '../utils/errorUtils';

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
    const message = extractApiErrorMessage(error, 'An unexpected error occurred');
    return new Error(message);
  }
}

export const awsAccountService = new AWSAccountService();