import axios from 'axios';

const isLocalhost =
  typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname.startsWith('192.168.') ||
    window.location.hostname.startsWith('10.'));

const DEFAULT_API_URL = isLocalhost
  ? 'http://127.0.0.1:8000/api/v1'
  : 'https://sportiq-2.onrender.com/api/v1';

const API_BASE_URL = import.meta.env.VITE_API_URL || DEFAULT_API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request Interceptor: Attach JWT Bearer Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sportiq_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle APIResponse envelope and 401 Logout
api.interceptors.response.use(
  (response) => {
    // Backend wraps data in { success: true, message: "...", data: {...} }
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sportiq_token');
      localStorage.removeItem('sportiq_user');
    }
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      'Network error. Please check if the server is running.';
    return Promise.reject(new Error(message));
  }
);

export default api;
