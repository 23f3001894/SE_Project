// Mock Data for AgriFlow E-commerce Application
// This file simulates backend API responses

// Current date for expiry calculations
const today = new Date();
const nextMonth = new Date(today);
nextMonth.setMonth(today.getMonth() + 1);
const lastMonth = new Date(today);
lastMonth.setMonth(today.getMonth() - 1);
const twoMonthsAgo = new Date(today);
twoMonthsAgo.setMonth(today.getMonth() - 2);

// Mock Users
export const mockUsers = [
  {
    id: 1,
    name: 'Admin User',
    email: 'admin@agriflow.com',
    password: 'admin123',
    role: 'admin',
    mobile_no: '9876543210'
  },
  {
    id: 2,
    name: 'John Farmer',
    email: 'john@farmer.com',
    password: 'customer123',
    role: 'customer',
    mobile_no: '9876543211',
    no_of_orders: 5
  },
  {
    id: 3,
    name: 'Jane Retailer',
    email: 'jane@retailer.com',
    password: 'customer123',
    role: 'customer',
    mobile_no: '9876543212',
    no_of_orders: 8
  }
];

// Mock Products (Fertilizers)
export const mockProducts = [
  {
    id: 1,
    name: 'Urea (Nitrogen Fertilizer) - 50kg',
    description: 'High nitrogen content fertilizer for promoting healthy leaf growth. Suitable for all crops.',
    price: 350,
    quantity: 100,
    expiry_date: nextMonth.toISOString().split('T')[0],
    expiry_status: 'expiring_soon',
    category: 'Nitrogen Fertilizers'
  },
  {
    id: 2,
    name: 'DAP (Di-Ammonium Phosphate) - 50kg',
    description: 'Phosphate-rich fertilizer ideal for root development and flowering stage.',
    price: 1350,
    quantity: 50,
    expiry_date: new Date(today.getTime() + 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    expiry_status: 'expiring_soon',
    category: 'Phosphate Fertilizers'
  },
  {
    id: 3,
    name: 'Potash (Muriate of Potash) - 50kg',
    description: 'Potassium-rich fertilizer for improving crop quality and disease resistance.',
    price: 900,
    quantity: 200,
    expiry_date: new Date(today.getTime() + 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    expiry_status: 'valid',
    category: 'Potash Fertilizers'
  },
  {
    id: 4,
    name: 'NPK 10-26-26 - 50kg',
    description: 'Balanced fertilizer with nitrogen, phosphorus, and potassium for overall plant health.',
    price: 1200,
    quantity: 75,
    expiry_date: new Date(today.getTime() + 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    expiry_status: 'valid',
    category: 'NPK Fertilizers'
  },
  {
    id: 5,
    name: 'Vermicompost (Organic) - 25kg',
    description: '100% organic compost rich in micronutrients. Improves soil health naturally.',
    price: 450,
    quantity: 30,
    expiry_date: lastMonth.toISOString().split('T')[0],
    expiry_status: 'expired',
    category: 'Organic Fertilizers'
  },
  {
    id: 6,
    name: 'Neem Cake - 25kg',
    description: 'Organic pest repellent and soil enricher. Natural way to protect your crops.',
    price: 380,
    quantity: 80,
    expiry_date: new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    expiry_status: 'expiring_soon',
    category: 'Organic Fertilizers'
  },
  {
    id: 7,
    name: 'NPK 19-19-19 - 50kg',
    description: 'Balanced water-soluble fertilizer for foliar application and drip irrigation.',
    price: 1450,
    quantity: 150,
    expiry_date: new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    expiry_status: 'valid',
    category: 'NPK Fertilizers'
  },
  {
    id: 8,
    name: 'Calcium Nitrate - 25kg',
    description: 'Fast-acting calcium source for preventing blossom end rot in vegetables.',
    price: 680,
    quantity: 60,
    expiry_date: new Date(today.getTime() + 45 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    expiry_status: 'valid',
    category: 'Specialty Fertilizers'
  }
];

// Mock Cart Items (per user)
export const mockCartItems = {
  2: [
    { cart_item_id: 1, product_id: 1, product_name: 'Organic Tomatoes', price: 45, quantity: 2, total_price: 90 },
    { cart_item_id: 2, product_id: 3, product_name: 'Basmati Rice (1kg)', price: 120, quantity: 1, total_price: 120 }
  ],
  3: [
    { cart_item_id: 3, product_id: 2, product_name: 'Green Apples', price: 80, quantity: 3, total_price: 240 }
  ]
};

// Mock Addresses (per user)
export const mockAddresses = {
  2: [
    {
      id: 1,
      address_line_1: '123 Farm Road',
      address_line_2: 'Village Rampur',
      city: 'Pune',
      state: 'Maharashtra',
      pin_code: '411001',
      is_default: true
    },
    {
      id: 2,
      address_line_1: '456 Market Area',
      address_line_2: 'Near Bus Stand',
      city: 'Mumbai',
      state: 'Maharashtra',
      pin_code: '400001',
      is_default: false
    }
  ],
  3: [
    {
      id: 3,
      address_line_1: '789 Shop No. 5',
      address_line_2: 'City Center Mall',
      city: 'Delhi',
      state: 'Delhi',
      pin_code: '110001',
      is_default: true
    }
  ]
};

// Mock Orders (per user)
export const mockOrders = {
  2: [
    {
      id: 101,
      customer_name: 'John Farmer',
      booking_date: twoMonthsAgo.toISOString(),
      total_price: 350,
      status: 'delivered',
      mode_of_payment: 'cash',
      delivery_date: lastMonth.toISOString().split('T')[0],
      delivery_address: {
        address_line_1: '123 Farm Road',
        city: 'Pune',
        state: 'Maharashtra',
        pin_code: '411001'
      },
      items: [
        { product_name: 'Potatoes (5kg bag)', quantity: 1, total_price: 150 },
        { product_name: 'Onions (3kg)', quantity: 1, total_price: 90 },
        { product_name: 'Wheat Flour (1kg)', quantity: 2, total_price: 130 }
      ]
    },
    {
      id: 102,
      customer_name: 'John Farmer',
      booking_date: lastMonth.toISOString(),
      total_price: 210,
      status: 'delivered',
      mode_of_payment: 'credit',
      delivery_date: lastMonth.toISOString().split('T')[0],
      delivery_address: {
        address_line_1: '123 Farm Road',
        city: 'Pune',
        state: 'Maharashtra',
        pin_code: '411001'
      },
      items: [
        { product_name: 'Green Apples', quantity: 2, total_price: 160 },
        { product_name: 'Bananas (dozen)', quantity: 1, total_price: 50 }
      ]
    }
  ],
  3: [
    {
      id: 201,
      customer_name: 'Jane Retailer',
      booking_date: lastMonth.toISOString(),
      total_price: 1500,
      status: 'delivered',
      mode_of_payment: 'credit',
      delivery_date: twoMonthsAgo.toISOString().split('T')[0],
      delivery_address: {
        address_line_1: '789 Shop No. 5',
        city: 'Delhi',
        state: 'Delhi',
        pin_code: '110001'
      },
      items: [
        { product_name: 'Basmati Rice (1kg)', quantity: 10, total_price: 1200 },
        { product_name: 'Wheat Flour (1kg)', quantity: 5, total_price: 325 }
      ]
    }
  ],
  admin: [
    {
      id: 101,
      customer_name: 'John Farmer',
      booking_date: twoMonthsAgo.toISOString(),
      total_price: 350,
      status: 'delivered',
      mode_of_payment: 'cash',
      delivery_date: lastMonth.toISOString().split('T')[0]
    },
    {
      id: 102,
      customer_name: 'John Farmer',
      booking_date: lastMonth.toISOString(),
      total_price: 210,
      status: 'delivered',
      mode_of_payment: 'credit',
      delivery_date: lastMonth.toISOString().split('T')[0]
    },
    {
      id: 201,
      customer_name: 'Jane Retailer',
      booking_date: lastMonth.toISOString(),
      total_price: 1500,
      status: 'delivered',
      mode_of_payment: 'credit',
      delivery_date: twoMonthsAgo.toISOString().split('T')[0]
    },
    {
      id: 202,
      customer_name: 'Jane Retailer',
      booking_date: today.toISOString(),
      total_price: 450,
      status: 'pending',
      mode_of_payment: 'cash',
      delivery_date: nextMonth.toISOString().split('T')[0]
    }
  ]
};

// Mock Reviews
export const mockReviews = {
  1: [
    { id: 1, user_name: 'John Farmer', rating: 5, review: 'Excellent nitrogen content! My crops have never looked better.' },
    { id: 2, user_name: 'Jane Retailer', rating: 4, review: 'Good quality urea, delivered on time.' }
  ],
  2: [
    { id: 3, user_name: 'John Farmer', rating: 5, review: 'Great DAP for root development. Will buy again!' }
  ],
  3: [
    { id: 4, user_name: 'Jane Retailer', rating: 5, review: 'Best potash in the market. Highly recommended for flowering crops.' }
  ]
};

// Mock Admin Dashboard Stats
export const mockAdminStats = {
  total_products: 8,
  total_users: 3,
  total_orders: 4,
  expiring_soon: 3,
  expired_products: 1,
  low_stock: 2
};

// Mock Top Customers
export const mockTopCustomers = [
  { id: 3, name: 'Jane Retailer', email: 'jane@retailer.com', no_of_orders: 8, total_spent: 1500 },
  { id: 2, name: 'John Farmer', email: 'john@farmer.com', no_of_orders: 5, total_spent: 560 }
];

// Mock Credit Scores
export const mockCreditScores = [
  { id: 2, name: 'John Farmer', total_spent: 560, total_paid: 350 },
  { id: 3, name: 'Jane Retailer', total_spent: 1500, total_paid: 0 }
];

// Mock High Demand Products
export const mockHighDemandProducts = [
  { product_id: 3, product_name: 'Potash (Muriate of Potash) - 50kg', units_sold_last_30_days: 45, demand_level: 'high', recommended_action: 'Increase stock by 50%' },
  { product_id: 7, product_name: 'NPK 19-19-19 - 50kg', units_sold_last_30_days: 38, demand_level: 'high', recommended_action: 'Ensure adequate supply for Rabi season' },
  { product_id: 1, product_name: 'Urea (Nitrogen Fertilizer) - 50kg', units_sold_last_30_days: 25, demand_level: 'medium', recommended_action: 'Maintain current stock levels' }
];

// Mock Monthly Sales Reports
export const mockMonthlySales = [
  { month: 'January', year: 2026, totalSales: 125000, orderCount: 45, topProduct: 'Urea (Nitrogen Fertilizer) - 50kg', customers: 12 },
  { month: 'February', year: 2026, totalSales: 98000, orderCount: 38, topProduct: 'DAP (Di-Ammonium Phosphate) - 50kg', customers: 10 },
  { month: 'March', year: 2026, totalSales: 156000, orderCount: 52, topProduct: 'NPK 19-19-19 - 50kg', customers: 15 }
];

// Mock Daily Sales for current month
export const mockDailySales = [
  { date: '2026-03-01', sales: 4500, orders: 2 },
  { date: '2026-03-02', sales: 8200, orders: 4 },
  { date: '2026-03-03', sales: 3200, orders: 1 },
  { date: '2026-03-04', sales: 12500, orders: 6 },
  { date: '2026-03-05', sales: 9800, orders: 5 },
  { date: '2026-03-06', sales: 15000, orders: 7 },
  { date: '2026-03-07', sales: 6700, orders: 3 },
  { date: '2026-03-08', sales: 4200, orders: 2 },
  { date: '2026-03-09', sales: 8900, orders: 4 },
  { date: '2026-03-10', sales: 11200, orders: 5 },
  { date: '2026-03-11', sales: 7600, orders: 3 },
  { date: '2026-03-12', sales: 13400, orders: 6 },
  { date: '2026-03-13', sales: 5400, orders: 2 },
  { date: '2026-03-14', sales: 9200, orders: 4 },
  { date: '2026-03-15', sales: 16800, orders: 8 }
];

// Mock Forecast Data
export const mockForecastData = {
  product_name: 'Potash (Muriate of Potash) - 50kg',
  method: 'Moving Average',
  historical_data_points: 90,
  forecast: [
    { month: today.getMonth() + 1, year: today.getFullYear(), predicted_quantity: 52, confidence: 'high' },
    { month: today.getMonth() + 2, year: today.getFullYear(), predicted_quantity: 58, confidence: 'medium' },
    { month: today.getMonth() + 3, year: today.getFullYear(), predicted_quantity: 65, confidence: 'low' }
  ]
};

// Helper function to calculate expiry status
export const calculateExpiryStatus = (expiryDate) => {
  if (!expiryDate) return 'valid';
  const expiry = new Date(expiryDate);
  const diffTime = expiry - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return 'expired';
  if (diffDays <= 14) return 'expiring_soon';
  return 'valid';
};

// Simulate API delay
export const simulateDelay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));
