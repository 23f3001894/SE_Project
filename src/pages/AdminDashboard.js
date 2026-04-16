import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [expiringProducts, setExpiringProducts] = useState([]);
  const [expiredProducts, setExpiredProducts] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);
  const [creditScores, setCreditScores] = useState([]);
  const [monthlySales, setMonthlySales] = useState([]);
  const [dailySales, setDailySales] = useState([]);
  const [salesSummary, setSalesSummary] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [
        statsRes,
        expiringRes,
        expiredRes,
        topCustomersRes,
        ordersRes,
        creditRes,
        monthlyRes,
        dailyRes,
        summaryRes,
      ] = await Promise.all([
        backendApi.get('/admin/dashboard/stats'),
        backendApi.get('/admin/products/expiring'),
        backendApi.get('/admin/products/expired'),
        backendApi.get('/admin/customers/top'),
        backendApi.get('/bookings/history'),
        backendApi.get('/admin/customers/credit-scores'),
        backendApi.get('/admin/reports/monthly-sales'),
        backendApi.get('/admin/reports/daily-sales'),
        backendApi.get('/admin/reports/summary'),
      ]);

      setStats(statsRes.data || {});
      setExpiringProducts(expiringRes.data.expiring_products || []);
      setExpiredProducts(expiredRes.data.expired_products || []);
      setTopCustomers(topCustomersRes.data.top_customers || []);
      setRecentOrders((ordersRes.data.bookings || []).slice(0, 5));
      setCreditScores(creditRes.data.customers || []);
      setMonthlySales(monthlyRes.data.monthly_sales || []);
      setDailySales(dailyRes.data.daily_sales || []);
      setSalesSummary(summaryRes.data || {});
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  if (loading) {
    return <div className="dashboard">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <div className="admin-dashboard dashboard-shell">
        <section className="page-hero admin-hero">
          <div>
            <p className="eyebrow">Seller command center</p>
            <h1>Welcome back, {user?.name}</h1>
            <p className="page-subtitle">
              Track your live inventory, monitor customer demand, and keep orders moving from checkout to delivery.
            </p>
          </div>
          <div className="hero-actions">
            <Link to="/products/create" className="btn">Add Product</Link>
            <Link to="/forecasting" className="btn btn-secondary">Demand Forecast</Link>
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card"><h3>Total Products</h3><p>{stats.total_products || 0}</p></div>
          <div className="stat-card"><h3>Total Buyers</h3><p>{stats.total_users || 0}</p></div>
          <div className="stat-card"><h3>Total Orders</h3><p>{stats.total_orders || 0}</p></div>
          <div className="stat-card"><h3>Expiring Soon</h3><p>{stats.expiring_soon || 0}</p></div>
          <div className="stat-card"><h3>Expired Products</h3><p>{stats.expired_products || 0}</p></div>
          <div className="stat-card"><h3>Low Stock</h3><p>{stats.low_stock || 0}</p></div>
        </section>

        <section className="sales-summary-cards">
          <div className="stat-card">
            <h3>Revenue This Month</h3>
            <p>Rs. {(salesSummary.total_revenue_this_month || 0).toFixed(2)}</p>
          </div>
          <div className="stat-card">
            <h3>Orders This Month</h3>
            <p>{salesSummary.total_orders_this_month || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Average Order Value</h3>
            <p>Rs. {(salesSummary.avg_order_value || 0).toFixed(2)}</p>
          </div>
          <div className="stat-card">
            <h3>Lifetime Revenue</h3>
            <p>Rs. {(salesSummary.total_revenue_all_time || 0).toFixed(2)}</p>
          </div>
        </section>

        <div className="dashboard-grid">
          <section className="section dashboard-panel">
            <h2>Recent Orders</h2>
            {recentOrders.length === 0 ? (
              <p>No recent orders.</p>
            ) : (
              <ul className="dashboard-list">
                {recentOrders.map((order) => (
                  <li key={order.id}>
                    <strong>Order #{order.id}</strong> for {order.customer_name} | Rs. {order.total_price}
                    <span className={`order-status ${order.status}`}>{order.status}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="section dashboard-panel">
            <h2>Top Customers</h2>
            {topCustomers.length === 0 ? (
              <p>No customers yet.</p>
            ) : (
              <ul className="dashboard-list">
                {topCustomers.map((customer) => (
                  <li key={customer.id}>
                    <strong>{customer.name}</strong> | {customer.no_of_orders} orders | Rs. {(customer.total_spent || 0).toFixed(2)}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="section dashboard-panel">
            <h2>Expiring Products</h2>
            {expiringProducts.length === 0 ? (
              <p>No products expiring soon.</p>
            ) : (
              <ul className="dashboard-list">
                {expiringProducts.map((product) => (
                  <li key={product.id}>
                    <strong>{product.name}</strong> | {product.quantity} units | {product.days_until_expiry} days left
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="section dashboard-panel">
            <h2>Expired Products</h2>
            {expiredProducts.length === 0 ? (
              <p>No expired products.</p>
            ) : (
              <ul className="dashboard-list">
                {expiredProducts.map((product) => (
                  <li key={product.id}>
                    <strong>{product.name}</strong> | expired on {product.expiry_date ? new Date(product.expiry_date).toLocaleDateString() : 'N/A'}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <section className="section dashboard-panel">
          <h2>Customer Credit Usage</h2>
          {creditScores.length === 0 ? (
            <p>No customer credit data available.</p>
          ) : (
            <ul className="dashboard-list">
              {creditScores.map((customer) => (
                <li key={customer.id}>
                  <strong>{customer.name}</strong> | outstanding Rs. {((customer.total_spent || 0) - (customer.total_paid || 0)).toFixed(2)}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="sales-reports-section">
          <h2>Sales Trends</h2>
          <div className="dashboard-grid">
            <div className="section dashboard-panel">
              <h3>Monthly Sales</h3>
              {monthlySales.length === 0 ? (
                <p>No monthly sales data available.</p>
              ) : (
                <table className="sales-table">
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Orders</th>
                      <th>Revenue</th>
                      <th>Growth</th>
                    </tr>
                  </thead>
                  <tbody>
                    {monthlySales.map((sale) => (
                      <tr key={sale.month}>
                        <td>{sale.month}</td>
                        <td>{sale.orders}</td>
                        <td>Rs. {sale.revenue.toFixed(2)}</td>
                        <td className={sale.growth >= 0 ? 'positive' : 'negative'}>
                          {sale.growth >= 0 ? '+' : ''}{sale.growth.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div className="section dashboard-panel">
              <h3>Daily Sales</h3>
              {dailySales.length === 0 ? (
                <p>No daily sales data available.</p>
              ) : (
                <table className="sales-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Orders</th>
                      <th>Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dailySales.map((sale) => (
                      <tr key={sale.date}>
                        <td>{sale.date}</td>
                        <td>{sale.orders}</td>
                        <td>Rs. {sale.revenue.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </section>
      </div>
    </>
  );
};

export default AdminDashboard;
