// Mock API Service - Intercepts axios calls and returns mock data
// This allows the frontend to work without a backend server

import { 
  mockUsers, 
  mockProducts, 
  mockCartItems, 
  mockAddresses, 
  mockOrders,
  mockReviews,
  mockAdminStats,
  mockTopCustomers,
  mockCreditScores,
  mockHighDemandProducts,
  mockForecastData,
  mockMonthlySales,
  mockDailySales,
  simulateDelay,
  calculateExpiryStatus
} from '../data/mockData';

// Local state for mutable data (cart, orders, products)
let products = [...mockProducts];
let cartItems = JSON.parse(JSON.stringify(mockCartItems));
let orders = JSON.parse(JSON.stringify(mockOrders));
let addresses = JSON.parse(JSON.stringify(mockAddresses));
let nextOrderId = 203;
let nextCartItemId = 4;
let nextAddressId = 4;

// Helper to get user from headers (case-insensitive)
const getUserFromHeaders = (headers) => {
  // HTTP headers are case-insensitive, so we need to handle different cases
  const userId = headers['User-Id'] || headers['user-id'] || headers['USER-ID'];
  const role = headers['Role'] || headers['role'] || headers['ROLE'];
  return { id: parseInt(userId), role };
};

// Auth API
export const mockAuthAPI = {
  login: async (email, password, role) => {
    console.log('Mock login called with:', email, password, role);
    await simulateDelay(300);
    // Find user by email and password (role is optional for demo purposes)
    const user = mockUsers.find(u => u.email === email && u.password === password);
    console.log('Found user:', user);
    if (!user) {
      throw { response: { data: { message: 'Invalid credentials' } } };
    }
    return {
      data: {
        user_id: user.id,
        role: user.role,
        name: user.name,
        email: user.email,
        mobile_no: user.mobile_no
      }
    };
  },

  register: async (userData) => {
    await simulateDelay(300);
    const existingUser = mockUsers.find(u => u.email === userData.email);
    if (existingUser) {
      throw { response: { data: { message: 'Email already registered' } } };
    }
    return { data: { message: 'Registration successful! Please login.' } };
  }
};

// Products API
export const mockProductsAPI = {
  getAll: async (role) => {
    await simulateDelay(200);
    // Update expiry statuses
    const updatedProducts = products.map(p => ({
      ...p,
      expiry_status: calculateExpiryStatus(p.expiry_date)
    }));
    return { data: { products: updatedProducts } };
  },

  getById: async (id, role) => {
    await simulateDelay(200);
    const product = products.find(p => p.id === parseInt(id));
    if (!product) {
      throw { response: { data: { message: 'Product not found' } } };
    }
    return { data: { product: { ...product, expiry_status: calculateExpiryStatus(product.expiry_date) } } };
  },

  create: async (productData, headers) => {
    await simulateDelay(300);
    const newProduct = {
      id: products.length + 1,
      ...productData,
      expiry_status: calculateExpiryStatus(productData.expiry_date)
    };
    products.push(newProduct);
    return { data: { message: 'Product created successfully', product: newProduct } };
  },

  update: async (id, productData, headers) => {
    await simulateDelay(300);
    const index = products.findIndex(p => p.id === parseInt(id));
    if (index === -1) {
      throw { response: { data: { message: 'Product not found' } } };
    }
    products[index] = {
      ...products[index],
      ...productData,
      expiry_status: calculateExpiryStatus(productData.expiry_date || products[index].expiry_date)
    };
    return { data: { message: 'Product updated successfully', product: products[index] } };
  },

  delete: async (id, headers) => {
    await simulateDelay(300);
    const index = products.findIndex(p => p.id === parseInt(id));
    if (index === -1) {
      throw { response: { data: { message: 'Product not found' } } };
    }
    products.splice(index, 1);
    return { data: { message: 'Product deleted successfully' } };
  }
};

// Cart API
export const mockCartAPI = {
  get: async (headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    const userCart = cartItems[id] || [];
    const totalPrice = userCart.reduce((sum, item) => sum + item.total_price, 0);
    return { data: { cart_items: userCart, total_price: totalPrice } };
  },

  add: async (productId, quantity, headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    const product = products.find(p => p.id === parseInt(productId));
    if (!product) {
      throw { response: { data: { message: 'Product not found' } } };
    }
    
    if (!cartItems[id]) {
      cartItems[id] = [];
    }
    
    const existingItem = cartItems[id].find(item => item.product_id === parseInt(productId));
    if (existingItem) {
      existingItem.quantity += quantity;
      existingItem.total_price = existingItem.price * existingItem.quantity;
    } else {
      cartItems[id].push({
        cart_item_id: nextCartItemId++,
        product_id: product.id,
        product_name: product.name,
        price: product.price,
        quantity: quantity,
        total_price: product.price * quantity
      });
    }
    
    return { data: { message: 'Item added to cart' } };
  },

  update: async (cartItemId, quantity, headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    const userCart = cartItems[id] || [];
    const item = userCart.find(i => i.cart_item_id === parseInt(cartItemId));
    
    if (!item) {
      throw { response: { data: { message: 'Item not found in cart' } } };
    }
    
    if (quantity <= 0) {
      // Remove item
      const index = userCart.indexOf(item);
      userCart.splice(index, 1);
    } else {
      item.quantity = quantity;
      item.total_price = item.price * quantity;
    }
    
    return { data: { message: 'Cart updated' } };
  },

  remove: async (cartItemId, headers) => {
    await simulateDelay(200);
    console.log('Mock cart remove called with cartItemId:', cartItemId, 'headers:', headers);
    const { id } = getUserFromHeaders(headers);
    console.log('User ID from headers:', id);
    
    if (!id) {
      throw { response: { data: { message: 'User ID not found in headers. Please log in again.' } } };
    }
    
    const userCart = cartItems[id] || [];
    console.log('User cart:', userCart);
    const index = userCart.findIndex(i => i.cart_item_id === parseInt(cartItemId));
    console.log('Item index:', index);
    
    if (index === -1) {
      throw { response: { data: { message: 'Item not found in cart' } } };
    }
    
    userCart.splice(index, 1);
    return { data: { message: 'Item removed from cart' } };
  }
};

// Bookings/Orders API
export const mockBookingsAPI = {
  getHistory: async (headers) => {
    await simulateDelay(200);
    const { id, role } = getUserFromHeaders(headers);
    
    let userOrders;
    if (role === 'admin') {
      userOrders = orders.admin || [];
    } else {
      userOrders = orders[id] || [];
    }
    
    return { data: { bookings: userOrders } };
  },

  create: async (bookingData, headers) => {
    console.log('Mock create booking called with:', bookingData, headers);
    await simulateDelay(300);
    const { id } = getUserFromHeaders(headers);
    const userCart = cartItems[id] || [];
    const userAddresses = addresses[id] || [];
    
    if (userCart.length === 0) {
      throw { response: { data: { message: 'Cart is empty' } } };
    }
    
    const selectedAddress = userAddresses.find(a => a.id === parseInt(bookingData.delivery_address_id));
    const totalPrice = userCart.reduce((sum, item) => sum + item.total_price, 0);
    
    const newOrder = {
      id: nextOrderId++,
      customer_name: 'Customer',
      booking_date: new Date().toISOString(),
      total_price: totalPrice,
      status: 'pending',
      mode_of_payment: bookingData.mode_of_payment,
      delivery_date: bookingData.delivery_date || null,
      delivery_address: selectedAddress || null,
      items: userCart.map(item => ({
        product_name: item.product_name,
        quantity: item.quantity,
        total_price: item.total_price
      }))
    };
    
    // Add to user's orders
    if (!orders[id]) {
      orders[id] = [];
    }
    orders[id].push(newOrder);
    orders.admin.push(newOrder);
    
    // Reduce product quantity (inventory)
    userCart.forEach(item => {
      const productIndex = products.findIndex(p => p.id === item.product_id);
      if (productIndex !== -1) {
        products[productIndex].quantity = Math.max(0, products[productIndex].quantity - item.quantity);
      }
    });
    
    // Clear cart
    cartItems[id] = [];
    
    return { 
      data: { 
        message: 'Order placed successfully',
        booking_id: newOrder.id,
        total_price: newOrder.total_price
      } 
    };
  }
};

// Addresses API
export const mockAddressesAPI = {
  getAll: async (headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    const userAddresses = addresses[id] || [];
    return { data: { addresses: userAddresses } };
  },

  create: async (addressData, headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    
    if (!addresses[id]) {
      addresses[id] = [];
    }
    
    // If this is the first address, make it default
    if (addresses[id].length === 0) {
      addressData.is_default = true;
    }
    
    const newAddress = {
      id: nextAddressId++,
      ...addressData
    };
    
    addresses[id].push(newAddress);
    return { data: { message: 'Address saved successfully', address: newAddress } };
  },

  update: async (addressId, addressData, headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    const userAddresses = addresses[id] || [];
    const index = userAddresses.findIndex(a => a.id === parseInt(addressId));
    
    if (index === -1) {
      throw { response: { data: { message: 'Address not found' } } };
    }
    
    // If setting as default, unset other defaults
    if (addressData.is_default) {
      userAddresses.forEach(a => a.is_default = false);
    }
    
    userAddresses[index] = { ...userAddresses[index], ...addressData };
    return { data: { message: 'Address updated successfully' } };
  },

  delete: async (addressId, headers) => {
    await simulateDelay(200);
    const { id } = getUserFromHeaders(headers);
    const userAddresses = addresses[id] || [];
    const index = userAddresses.findIndex(a => a.id === parseInt(addressId));
    
    if (index === -1) {
      throw { response: { data: { message: 'Address not found' } } };
    }
    
    userAddresses.splice(index, 1);
    return { data: { message: 'Address deleted successfully' } };
  }
};

// Reviews API
export const mockReviewsAPI = {
  getByProduct: async (productId, role) => {
    await simulateDelay(200);
    const reviews = mockReviews[parseInt(productId)] || [];
    return { data: { reviews } };
  }
};

// Admin API
export const mockAdminAPI = {
  getDashboardStats: async (role) => {
    await simulateDelay(200);
    return { data: mockAdminStats };
  },

  getExpiringProducts: async (role) => {
    await simulateDelay(200);
    const expiringProducts = products
      .filter(p => calculateExpiryStatus(p.expiry_date) === 'expiring_soon')
      .map(p => {
        const expiry = new Date(p.expiry_date);
        const diffTime = expiry - new Date();
        const daysUntilExpiry = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return { ...p, days_until_expiry: daysUntilExpiry };
      });
    return { data: { expiring_products: expiringProducts } };
  },

  getExpiredProducts: async (role) => {
    await simulateDelay(200);
    const expiredProducts = products.filter(p => calculateExpiryStatus(p.expiry_date) === 'expired');
    return { data: { expired_products: expiredProducts } };
  },

  getTopCustomers: async (role) => {
    await simulateDelay(200);
    return { data: { top_customers: mockTopCustomers } };
  },

  getCreditScores: async (role) => {
    await simulateDelay(200);
    return { data: { customers: mockCreditScores } };
  },

  getHighDemandRecommendations: async (role) => {
    await simulateDelay(200);
    return { data: { high_demand_recommendations: mockHighDemandProducts } };
  },

  getForecast: async (productId, monthsAhead, role) => {
    await simulateDelay(500);
    const product = products.find(p => p.id === parseInt(productId));
    if (!product) {
      throw { response: { data: { message: 'Product not found' } } };
    }
    return { data: { ...mockForecastData, product_name: product.name } };
  },

  // Sales Reports
  getMonthlySales: async (role) => {
    await simulateDelay(300);
    // Transform to include month name, revenue, orders, and growth
    const monthly_sales = mockMonthlySales.map((m, index) => ({
      month: `${m.month} ${m.year}`,
      revenue: m.totalSales,
      orders: m.orderCount,
      growth: index === 0 ? 0 : ((m.totalSales - mockMonthlySales[index - 1].totalSales) / mockMonthlySales[index - 1].totalSales) * 100
    }));
    return { data: { monthly_sales } };
  },

  getDailySales: async (role) => {
    await simulateDelay(300);
    // Transform daily sales data - mockDailySales uses 'sales' not 'totalSales'
    const daily_sales = mockDailySales.slice(-7).map(d => ({
      date: d.date,
      revenue: d.sales,
      orders: d.orders
    }));
    return { data: { daily_sales } };
  },

  getSalesSummary: async (role) => {
    await simulateDelay(200);
    const totalRevenueAllTime = mockMonthlySales.reduce((sum, m) => sum + m.totalSales, 0);
    const totalOrdersThisMonth = mockMonthlySales.reduce((sum, m) => sum + m.orderCount, 0);
    const totalRevenueThisMonth = mockMonthlySales[mockMonthlySales.length - 1]?.totalSales || 0;
    const avgOrderValue = totalRevenueAllTime / totalOrdersThisMonth;
    return { data: { 
      total_revenue_this_month: totalRevenueThisMonth,
      total_orders_this_month: totalOrdersThisMonth,
      total_revenue_all_time: totalRevenueAllTime,
      avg_order_value: avgOrderValue
    }};
  }
};

// Create a mock axios instance
export const createMockAxios = () => {
  return {
    get: async (url, config = {}) => {
      console.log('Mock GET called with URL:', url);
      const headers = config.headers || {};
      const urlParts = url.split('/');
      
      // Products
      if (url === '/products/' || url === '/api/products/' || url === 'http://localhost:5000/api/products/') {
        return mockProductsAPI.getAll(headers['Role']);
      }
      if (url.match(/\/products\/\d+/) || url.match(/\/api\/products\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/products\/\d+/)) {
        const id = url.match(/\/products\/(\d+)/)?.[1] || url.match(/\/api\/products\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockProductsAPI.getById(id, headers['Role']);
      }
      
      // Cart
      if (url === '/cart/' || url === '/api/cart/' || url === 'http://localhost:5000/api/cart/') {
        return mockCartAPI.get(headers);
      }
      
      // Bookings/Orders
      if (url === '/bookings/history' || url === '/api/bookings/history' || url === 'http://localhost:5000/api/bookings/history') {
        return mockBookingsAPI.getHistory(headers);
      }
      
      // Addresses
      if (url === '/addresses/' || url === '/api/addresses/' || url === 'http://localhost:5000/api/addresses/') {
        return mockAddressesAPI.getAll(headers);
      }
      
      // Reviews
      if (url.match(/\/reviews\/product\/\d+/) || url.match(/\/api\/reviews\/product\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/reviews\/product\/\d+/)) {
        const productId = url.match(/\/reviews\/product\/(\d+)/)?.[1] || url.match(/\/api\/reviews\/product\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockReviewsAPI.getByProduct(productId, headers['Role']);
      }
      
      // Admin Dashboard
      if (url === '/admin/dashboard/stats' || url === '/api/admin/dashboard/stats' || url === 'http://localhost:5000/api/admin/dashboard/stats') {
        return mockAdminAPI.getDashboardStats(headers['Role']);
      }
      if (url === '/admin/products/expiring' || url === '/api/admin/products/expiring' || url === 'http://localhost:5000/api/admin/products/expiring') {
        return mockAdminAPI.getExpiringProducts(headers['Role']);
      }
      if (url === '/admin/products/expired' || url === '/api/admin/products/expired' || url === 'http://localhost:5000/api/admin/products/expired') {
        return mockAdminAPI.getExpiredProducts(headers['Role']);
      }
      if (url === '/admin/customers/top' || url === '/api/admin/customers/top' || url === 'http://localhost:5000/api/admin/customers/top') {
        return mockAdminAPI.getTopCustomers(headers['Role']);
      }
      if (url === '/admin/customers/credit-scores' || url === '/api/admin/customers/credit-scores' || url === 'http://localhost:5000/api/admin/customers/credit-scores') {
        return mockAdminAPI.getCreditScores(headers['Role']);
      }
      if (url === '/admin/recommendations/high-demand' || url === '/api/admin/recommendations/high-demand' || url === 'http://localhost:5000/api/admin/recommendations/high-demand') {
        return mockAdminAPI.getHighDemandRecommendations(headers['Role']);
      }
      
      // Sales Reports
      if (url === '/admin/reports/monthly-sales' || url === '/api/admin/reports/monthly-sales' || url === 'http://localhost:5000/api/admin/reports/monthly-sales') {
        return mockAdminAPI.getMonthlySales(headers['Role']);
      }
      if (url === '/admin/reports/daily-sales' || url === '/api/admin/reports/daily-sales' || url === 'http://localhost:5000/api/admin/reports/daily-sales') {
        return mockAdminAPI.getDailySales(headers['Role']);
      }
      if (url === '/admin/reports/summary' || url === '/api/admin/reports/summary' || url === 'http://localhost:5000/api/admin/reports/summary') {
        return mockAdminAPI.getSalesSummary(headers['Role']);
      }
      
      // Forecast
      if (url.match(/\/admin\/forecast\/demand/) || url.match(/\/api\/admin\/forecast\/demand/) || url.match(/http:\/\/localhost:5000\/api\/admin\/forecast\/demand/)) {
        const params = new URL(url.split('?')[1] || '').searchParams;
        const productId = params.get('product_id');
        const monthsAhead = parseInt(params.get('months_ahead')) || 3;
        return mockAdminAPI.getForecast(productId, monthsAhead, headers['Role']);
      }
      
      throw new Error(`Mock GET not implemented for: ${url}`);
    },
    
    post: async (url, data = {}, config = {}) => {
      console.log('Mock POST called with URL:', url);
      const headers = config.headers || {};
      
      // Auth
      if (url === '/auth/login' || url === '/api/auth/login' || url === 'http://localhost:5000/api/auth/login') {
        return mockAuthAPI.login(data.email, data.password, headers['Role']);
      }
      if (url === '/auth/register' || url === '/api/auth/register' || url === 'http://localhost:5000/api/auth/register') {
        return mockAuthAPI.register(data);
      }
      
      // Products
      if (url === '/products/' || url === '/api/products/' || url === 'http://localhost:5000/api/products/') {
        return mockProductsAPI.create(data, headers);
      }
      
      // Cart
      if (url === '/cart/add' || url === '/api/cart/add' || url === 'http://localhost:5000/api/cart/add') {
        return mockCartAPI.add(data.product_id, data.quantity, headers);
      }
      
      // Bookings
      if (url === '/bookings/' || url === '/api/bookings/' || url === 'http://localhost:5000/api/bookings/') {
        return mockBookingsAPI.create(data, headers);
      }
      
      // Addresses
      if (url === '/addresses/' || url === '/api/addresses/' || url === 'http://localhost:5000/api/addresses/') {
        return mockAddressesAPI.create(data, headers);
      }
      
      // If no match, throw error with proper axios format
      throw {
        response: {
          data: {
            message: `Mock API not implemented for: ${url}`
          }
        }
      };
    },
    
    put: async (url, data = {}, config = {}) => {
      console.log('Mock PUT called with URL:', url);
      const headers = config.headers || {};
      const urlParts = url.split('/');
      
      // Cart
      if (url.match(/\/cart\/update\/\d+/) || url.match(/\/api\/cart\/update\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/cart\/update\/\d+/)) {
        const cartItemId = url.match(/\/cart\/update\/(\d+)/)?.[1] || url.match(/\/api\/cart\/update\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockCartAPI.update(cartItemId, data.quantity, headers);
      }
      
      // Addresses
      if (url.match(/\/addresses\/\d+/) || url.match(/\/api\/addresses\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/addresses\/\d+/)) {
        const addressId = url.match(/\/addresses\/(\d+)/)?.[1] || url.match(/\/api\/addresses\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockAddressesAPI.update(addressId, data, headers);
      }
      
      // Products
      if (url.match(/\/products\/\d+/) || url.match(/\/api\/products\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/products\/\d+/)) {
        const productId = url.match(/\/products\/(\d+)/)?.[1] || url.match(/\/api\/products\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockProductsAPI.update(productId, data, headers);
      }
      
      throw { response: { data: { message: `Mock PUT not implemented for: ${url}` } } };
    },
    
    delete: async (url, config = {}) => {
      console.log('Mock DELETE called with URL:', url);
      console.log('Mock DELETE config.headers:', config.headers);
      const headers = config.headers || {};
      const urlParts = url.split('/');
      
      // Products
      if (url.match(/\/products\/\d+/) || url.match(/\/api\/products\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/products\/\d+/)) {
        const productId = url.match(/\/products\/(\d+)/)?.[1] || url.match(/\/api\/products\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockProductsAPI.delete(productId, headers);
      }
      
      // Cart
      if (url.match(/\/cart\/remove\/\d+/) || url.match(/\/api\/cart\/remove\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/cart\/remove\/\d+/)) {
        const cartItemId = url.match(/\/cart\/remove\/(\d+)/)?.[1] || url.match(/\/api\/cart\/remove\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        console.log('Cart remove matched - cartItemId:', cartItemId);
        return mockCartAPI.remove(cartItemId, headers);
      }
      
      // Addresses
      if (url.match(/\/addresses\/\d+/) || url.match(/\/api\/addresses\/\d+/) || url.match(/http:\/\/localhost:5000\/api\/addresses\/\d+/)) {
        const addressId = url.match(/\/addresses\/(\d+)/)?.[1] || url.match(/\/api\/addresses\/(\d+)/)?.[1] || urlParts[urlParts.length - 1];
        return mockAddressesAPI.delete(addressId, headers);
      }
      
      throw { response: { data: { message: `Mock DELETE not implemented for: ${url}` } } };
    }
  };
};

export default createMockAxios;
