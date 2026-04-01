import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const OrderHistory = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrderHistory();
  }, [user]);

  const fetchOrderHistory = async () => {
    if (!user) return;
    try {
      const response = await api.get('/bookings/history', {
        headers: {
          'User-Id': user.user_id,
          'Role': user.role
        }
      });
      setOrders(response.data.bookings);
    } catch (err) {
      console.error('Error fetching order history:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="order-history">Loading...</div>;
  }

  const isAdmin = user?.role === 'admin';

  return (
    <>
      <Navbar />
      <div className="order-history">
        <h1>{isAdmin ? 'All Orders' : 'My Orders'}</h1>
        {orders.length === 0 ? (
          <div>
            {isAdmin ? (
              <p>No orders placed by customers yet.</p>
            ) : (
              <>
                <p>You haven't placed any orders yet.</p>
                <Link to="/products" className="btn">
                  Start Shopping
                </Link>
              </>
            )}
          </div>
        ) : (
          <>
            <h2>{isAdmin ? 'All Customer Orders' : 'Your Orders'}</h2>
            <div className="orders-list">
              {orders.map(order => (
                <div key={order.id} className="order-card">
                  <div className="order-header">
                    <h3>Order #{order.id}</h3>
                    {isAdmin && order.customer_name && (
                      <p className="customer-name"><strong>Customer:</strong> {order.customer_name}</p>
                    )}
                    <p className="order-date">{new Date(order.booking_date).toLocaleDateString()}</p>
                    <p className="order-status">{order.status}</p>
                  </div>
                  <div className="order-details">
                    <p><strong>Total:</strong> ₹{order.total_price}</p>
                    <p><strong>Payment Method:</strong> {order.mode_of_payment}</p>
                    <p><strong>Delivery Date:</strong> {order.delivery_date ? new Date(order.delivery_date).toLocaleDateString() : 'Not scheduled'}</p>
                  </div>
                  <div className="order-items">
                    <h4>Items:</h4>
                    <ul>
                      {order.items.map((item, idx) => (
                        <li key={idx}>
                          {item.product_name} x {item.quantity} = ₹{item.total_price}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="order-address">
                    <h4>Delivery Address:</h4>
                    <p>
                      {order.delivery_address?.address_line_1}, {order.delivery_address?.address_line_2}, 
                      {order.delivery_address?.city}, {order.delivery_address?.state} {order.delivery_address?.pin_code}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default OrderHistory;