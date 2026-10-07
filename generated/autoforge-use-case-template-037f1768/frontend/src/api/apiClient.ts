import axios from 'axios';
import { useAuth } from '../auth/AuthContext';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8080',
  timeout: 10000
});

// Request interceptor to attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
