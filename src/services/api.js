// API Service - Uses mock API by default for frontend-only operation
// To use real backend, set USE_MOCK_API = false

import axios from 'axios';
import { createMockAxios } from './mockApi';

const USE_MOCK_API = true; // Set to false to use real backend

// Create mock axios instance
const mockAxios = createMockAxios();

// Real axios instance for backend API
const realAxios = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Export the appropriate API based on USE_MOCK_API
const api = USE_MOCK_API ? mockAxios : realAxios;

export default api;

// Export both for direct use if needed
export { mockAxios, realAxios };
