// Utility functions for safely handling error objects in React components

/**
 * Safely extract error message from any error type
 * @param {any} error - Error object, string, or other value
 * @param {string} fallback - Fallback message if extraction fails
 * @returns {string} Safe string message for React rendering
 */
export const extractErrorMessage = (error, fallback = 'An unexpected error occurred') => {
  if (!error) {
    return fallback;
  }
  
  // If it's already a string
  if (typeof error === 'string') {
    return error;
  }
  
  // Handle Error objects
  if (error instanceof Error) {
    return error.message || fallback;
  }
  
  // Handle validation error arrays (FastAPI validation)
  if (Array.isArray(error)) {
    return error.map(err => {
      if (typeof err === 'string') return err;
      if (err && err.msg) return err.msg;
      return JSON.stringify(err);
    }).join(', ');
  }
  
  // Handle validation error objects (FastAPI validation)
  if (typeof error === 'object' && error !== null) {
    // Check for FastAPI validation error structure
    if (error.msg) {
      return error.msg;
    }
    
    // Check for common error message fields
    if (error.message) {
      return error.message;
    }
    
    if (error.detail) {
      // Recursively handle nested detail
      return extractErrorMessage(error.detail, fallback);
    }
    
    // Last resort: stringify the object
    try {
      return JSON.stringify(error);
    } catch {
      return fallback;
    }
  }
  
  return fallback;
};

/**
 * Extract error message from API response error
 * @param {any} apiError - Axios error object or similar
 * @param {string} fallback - Fallback message
 * @returns {string} Safe string message
 */
export const extractApiErrorMessage = (apiError, fallback = 'An API error occurred') => {
  if (!apiError) {
    return fallback;
  }
  
  // Check response data detail
  if (apiError.response && apiError.response.data && apiError.response.data.detail) {
    return extractErrorMessage(apiError.response.data.detail, fallback);
  }
  
  // Check direct message
  if (apiError.message) {
    return extractErrorMessage(apiError.message, fallback);
  }
  
  // Handle the error object itself
  return extractErrorMessage(apiError, fallback);
};