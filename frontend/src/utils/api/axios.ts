import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  // Increase timeout if needed
  timeout: 10000,
});

// Add request interceptor to add Authorization header
api.interceptors.request.use(
  (config) => {
    const accessToken = sessionStorage.getItem('accessToken');
    // console.log('Access Token:', sessionStorage.getItem('accessToken'));
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    // Log request for debugging
    // console.log('Request Config:', {
    //   url: config.url,
    //   method: config.method,
    //   headers: config.headers,
    //   params: config.params
    // });
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor with improved error handling
api.interceptors.response.use(
  (response) => {
    // Log successful response for debugging
    // console.log('Response:', response.data);
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with an error status
      console.error('Server Error:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error:', {
        request: error.request,
        message: error.message
      });
    } else {
      // Error in request configuration
      console.error('Request Config Error:', error.message);
    }
    return Promise.reject(error);
  }
);