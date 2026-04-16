import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';

const OrderHistory = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatingOrderId, setUpdatingOrderId] = useState(null);

  const fetchOrderHistory = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      const response = await backendApi.get('/bookings/history');
      setOrders(response.data.bookings || []);
    } catch (err) {
      console.error('Error fetching order history:', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchOrderHistory();
  }, [fetchOrderHistory]);

  const markDelivered = async (orderId) => {
    setUpdatingOrderId(orderId);
    try {
      await backendApi.put(`/admin/orders/${orderId}/deliver`);
      await fetchOrderHistory();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to mark order as delivered');
    } finally {
      setUpdatingOrderId(null);
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
        <h1>{isAdmin ? 'Orders For Your Products' : 'My Orders'}</h1>
        {orders.length === 0 ? (
          <div>
            {isAdmin ? (
              <p>No orders for your products yet.</p>
            ) : (
              <>
                <p>You have not placed any orders yet.</p>
                <Link to="/products" className="btn">
                  Start Shopping
                </Link>
              </>
            )}
          </div>
        ) : (
          <>
            <h2>{isAdmin ? 'Recent marketplace orders' : 'Your order history'}</h2>
            <div className="orders-list">
              {orders.map((order) => (
                <div key={order.id} className="order-card">
                  <div className="order-header">
                    <h3>Order #{order.id}</h3>
                    {isAdmin && order.customer_name && (
                      <p className="customer-name">
                        <strong>Customer:</strong> {order.customer_name}
                      </p>
                    )}
                    <p className="order-date">{new Date(order.booking_date).toLocaleDateString()}</p>
                    <p className={`order-status ${order.status}`}>{order.status}</p>
                  </div>
                  <div className="order-details">
                    <p><strong>Total:</strong> Rs. {order.total_price}</p>
                    <p><strong>Payment Method:</strong> {order.mode_of_payment}</p>
                    <p>
                      <strong>Delivery Date:</strong>{' '}
                      {order.delivery_date ? new Date(order.delivery_date).toLocaleDateString() : 'Not scheduled'}
                    </p>
                  </div>
                  <div className="order-items">
                    <h4>Items:</h4>
                    <ul>
                      {order.items.map((item, index) => (
                        <li key={`${order.id}-${index}`}>
                          {item.product_name} x {item.quantity} = Rs. {item.total_price}
                        </li>
                      ))}
                    </ul>
                  </div>
                  {isAdmin && order.status !== 'delivered' && (
                    <div className="order-actions">
                      <button
                        type="button"
                        className="btn"
                        onClick={() => markDelivered(order.id)}
                        disabled={updatingOrderId === order.id}
                      >
                        {updatingOrderId === order.id ? 'Updating...' : 'Mark as Delivered'}
                      </button>
                    </div>
                  )}
                  <div className="order-address">
                    <h4>Delivery Address:</h4>
                    <p>
                      {order.delivery_address?.address_line_1}, {order.delivery_address?.address_line_2},{' '}
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
