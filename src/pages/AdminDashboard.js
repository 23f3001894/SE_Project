import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [expiringProducts, setExpiringProducts] = useState([]);
  const [expiredProducts, setExpiredProducts] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);
  const [creditScores, setCreditScores] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, expiringRes, expiredRes, topCustomersRes, ordersRes, creditRes] = await Promise.all([
        api.get('/admin/dashboard/stats', {
          headers: { 'Role': 'admin' }
        }),
        api.get('/admin/products/expiring', {
          headers: { 'Role': 'admin' }
        }),
        api.get('/admin/products/expired', {
          headers: { 'Role': 'admin' }
        }),
        api.get('/admin/customers/top', {
          headers: { 'Role': 'admin' }
        }),
        api.get('/bookings/history', {
          headers: { 'Role': 'admin', 'User-ID': user?.id }
        }),
        api.get('/admin/customers/credit-scores', {
          headers: { 'Role': 'admin' }
        })
      ]);
      
      setStats(statsRes.data);
      setExpiringProducts(expiringRes.data.expiring_products);
      setExpiredProducts(expiredRes.data.expired_products);
      setTopCustomers(topCustomersRes.data.top_customers);
      // Get only the 5 most recent orders
      setRecentOrders(ordersRes.data.bookings?.slice(0, 5) || []);
      setCreditScores(creditRes.data.customers || []);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="dashboard">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      <p>Welcome, {user?.name}!</p>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Products</h3>
          <p>{stats.total_products || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Total Users</h3>
          <p>{stats.total_users || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Total Orders</h3>
          <p>{stats.total_orders || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Expiring Soon</h3>
          <p>{stats.expiring_soon || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Expired Products</h3>
          <p>{stats.expired_products || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Low Stock</h3>
          <p>{stats.low_stock || 0}</p>
        </div>
      </div>
      
      <div className="section">
        <h2>Expiring Soon Products</h2>
        {expiringProducts.length === 0 ? (
          <p>No products expiring soon.</p>
        ) : (
          <ul>
            {expiringProducts.map(product => (
              <li key={product.id}>
                {product.name} - {product.quantity} units - Expires in {product.days_until_expiry} days
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="section">
        <h2>Expired Products</h2>
        {expiredProducts.length === 0 ? (
          <p>No expired products.</p>
        ) : (
          <ul>
            {expiredProducts.map(product => (
              <li key={product.id}>
                {product.name} - {product.quantity} units - Expired on {new Date(product.expiry_date).toLocaleDateString()}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="section">
        <h2>Top Customers</h2>
        {topCustomers.length === 0 ? (
          <p>No customers yet.</p>
        ) : (
          <ul>
            {topCustomers.map(customer => (
              <li key={customer.id}>
                {customer.name} ({customer.email}) - {customer.no_of_orders} orders - ₹{customer.total_spent?.toFixed(2) || '0.00'}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="section">
        <h2>Customer Credit Usage</h2>
        {creditScores.length === 0 ? (
          <p>No customer credit data available.</p>
        ) : (
          <ul>
            {creditScores.map(customer => (
              <li key={customer.id}>
                {customer.name} - Credit Used: ₹{(customer.total_spent - (customer.total_paid || 0)).toFixed(2)}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="section">
        <h2>Recent Orders (Purchase Notifications)</h2>
        {recentOrders.length === 0 ? (
          <p>No recent orders.</p>
        ) : (
          <ul>
            {recentOrders.map(order => (
              <li key={order.id}>
                <strong>Order #{order.id}</strong> - {order.customer_name} - ₹{order.total_price} - 
                <span className={`order-status ${order.status}`}>{order.status}</span> - 
                {new Date(order.booking_date).toLocaleString()}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="quick-links">
        <h2>Quick Links</h2>
        <Link to="/products" className="btn">Manage Products</Link>
        <Link to="/orders" className="btn">View All Orders</Link>
        <Link to="/forecasting" className="btn">📊 Forecasting & Analytics</Link>
      </div>
    </div>
    </>
  );
};

export default AdminDashboard;