import { apiClient } from './api';

export const productionInfrastructureService = {
  // Create architecture from scratch
  createFromScratch: async (data) => {
    const response = await apiClient.post('/production-infrastructure/create-from-scratch', data);
    return response.data;
  },

  // Import existing infrastructure
  importExisting: async (data) => {
    const response = await apiClient.post('/production-infrastructure/import-existing', data);
    return response.data;
  },

  // Apply security policies
  applySecurityPolicies: async (data) => {
    const response = await apiClient.post('/production-infrastructure/apply-security-policies', data);
    return response.data;
  },

  // Get deployment status
  getDeploymentStatus: async (deploymentId) => {
    const response = await apiClient.get(`/production-infrastructure/deployment-status/${deploymentId}`);
    return response.data;
  },

  // Destroy deployment
  destroyDeployment: async (deploymentId, awsCredentials) => {
    const response = await apiClient.post(`/production-infrastructure/destroy-deployment/${deploymentId}`, {
      aws_credentials: awsCredentials
    });
    return response.data;
  },

  // Validate AWS credentials
  validateCredentials: async (credentials) => {
    const response = await apiClient.get('/production-infrastructure/validate-aws-credentials', {
      params: credentials
    });
    return response.data;
  }
};

export default productionInfrastructureService;