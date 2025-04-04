import axios, { AxiosError } from 'axios';

// Create axios instance
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    
    // If auth is enabled and we have a token, add it to requests
    if (import.meta.env.VITE_AUTH_ENABLED === 'true' && token) {
      config.headers['X-API-Key'] = token;
    } else if (import.meta.env.VITE_API_KEY) {
      // Default API key from environment
      config.headers['X-API-Key'] = import.meta.env.VITE_API_KEY;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 401) {
        // Unauthorized - redirect to login
        if (import.meta.env.VITE_AUTH_ENABLED === 'true') {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
      }
      
      // Extract error message from response if available
      const message = error.response.data && typeof error.response.data === 'object' && 'detail' in error.response.data
        ? error.response.data.detail
        : error.message;
        
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // The request was made but no response was received
      return Promise.reject(new Error('No response received from server. Please check your connection.'));
    } else {
      // Something happened in setting up the request that triggered an Error
      return Promise.reject(error);
    }
  }
);

export default api;