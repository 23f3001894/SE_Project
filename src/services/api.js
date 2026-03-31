// API Service - Configure for backend connection
// Set USE_MOCK_API = false to use real backend

import axios from 'axios';

// ============================================================================
// CONFIGURATION
// ============================================================================

const USE_MOCK_API = false; // Set to false to use real backend
const API_BASE_URL = 'http://localhost:5000/api';

// ============================================================================
// REAL API IMPLEMENTATION
// ============================================================================

// Create real axios instance with proper configuration
const realAxios = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth headers
realAxios.interceptors.request.use(
  (config) => {
    // Get user data from localStorage (set during login)
    const userData = localStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      config.headers['User-Id'] = user.user_id;
      config.headers['Role'] = user.role;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
realAxios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear local storage and redirect to login
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// MOCK API (for development without backend)
// ============================================================================

// Import mock API
import { createMockAxios } from './mockApi';
const mockAxios = createMockAxios();

// ============================================================================
// API EXPORTS
// ============================================================================

// Export the appropriate API based on configuration
const api = USE_MOCK_API ? mockAxios : realAxios;

// Export for direct use if needed
export { realAxios, mockAxios };

// ============================================================================
// CONVENIENCE METHODS
// ============================================================================

// Auth API
export const authAPI = {
  login: (email, password, role) => 
    api.post('/auth/login', { email, password }),
  
  register: (userData) => 
    api.post('/auth/register', userData),
};

// Products API
export const productsAPI = {
  getAll: () => api.get('/products/'),
  
  getById: (id) => api.get(`/products/${id}`),
  
  create: (productData) => api.post('/products/', productData),
  
  update: (id, productData) => api.put(`/products/${id}`, productData),
  
  delete: (id) => api.delete(`/products/${id}`),
};

// Cart API
export const cartAPI = {
  get: () => api.get('/cart/'),
  
  add: (productId, quantity) => 
    api.post('/cart/add', { product_id: productId, quantity }),
  
  update: (cartItemId, quantity) => 
    api.put(`/cart/update/${cartItemId}`, { quantity }),
  
  remove: (cartItemId) => api.delete(`/cart/remove/${cartItemId}`),
};

// Bookings/Orders API
export const bookingsAPI = {
  getHistory: () => api.get('/bookings/history'),
  
  create: (bookingData) => api.post('/bookings/', bookingData),
};

// Addresses API
export const addressesAPI = {
  getAll: () => api.get('/addresses/'),
  
  create: (addressData) => api.post('/addresses/', addressData),
  
  update: (addressId, addressData) => 
    api.put(`/addresses/${addressId}`, addressData),
  
  delete: (addressId) => api.delete(`/addresses/${addressId}`),
};

// Reviews API
export const reviewsAPI = {
  getByProduct: (productId) => api.get(`/reviews/product/${productId}`),
  
  create: (reviewData) => api.post('/reviews/', reviewData),
};

// Admin API
export const adminAPI = {
  // Dashboard
  getDashboardStats: () => api.get('/admin/dashboard/stats'),
  
  // Products
  getExpiringProducts: () => api.get('/admin/products/expiring'),
  
  getExpiredProducts: () => api.get('/admin/products/expired'),
  
  // Customers
  getTopCustomers: () => api.get('/admin/customers/top'),
  
  getCreditScores: () => api.get('/admin/customers/credit-scores'),
  
  // Recommendations
  getHighDemandRecommendations: () => 
    api.get('/admin/recommendations/high-demand'),
  
  // Sales Reports
  getMonthlySales: () => api.get('/admin/reports/monthly-sales'),
  
  getDailySales: () => api.get('/admin/reports/daily-sales'),
  
  getSalesSummary: () => api.get('/admin/reports/summary'),
  
  // Forecasting
  getForecast: (productId, monthsAhead = 3) => 
    api.get('/admin/forecast/demand', { 
      params: { product_id: productId, months_ahead: monthsAhead } 
    }),
};

// Default export
export default api;
