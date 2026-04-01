import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

const CartPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showCheckout, setShowCheckout] = useState(false);
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [paymentMode, setPaymentMode] = useState('cash');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchCart();
  }, [user]);

  const fetchCart = async () => {
    if (!user) return;
    try {
      const response = await api.get('/cart/', {
        headers: {
          'User-Id': user.user_id,
          'Role': user.role
        }
      });
      setCartItems(response.data.cart_items);
      setTotalPrice(response.data.total_price);
      
      // Fetch addresses for checkout
      fetchAddresses();
    } catch (err) {
      console.error('Error fetching cart:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAddresses = async () => {
    if (!user) return;
    try {
      const response = await api.get('/addresses/', {
        headers: {
          'User-Id': user.user_id,
          'Role': user.role
        }
      });
      setAddresses(response.data.addresses);
      if (response.data.addresses.length > 0) {
        setSelectedAddress(response.data.addresses[0].address_id?.toString() || response.data.addresses[0].id?.toString() || '');
      }
    } catch (err) {
      console.error('Error fetching addresses:', err);
    }
  };

  const updateQuantity = async (cartItemId, quantity) => {
    if (!user) return;
    try {
      await api.put(
        `/cart/update/${cartItemId}`,
        { quantity },
        {
          headers: {
            'User-Id': user.user_id,
            'Role': user.role
          }
        }
      );
      fetchCart();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to update cart');
    }
  };

  const removeFromCart = async (cartItemId) => {
    if (!user) return;
    if (!window.confirm('Remove item from cart?')) return;
    try {
      await api.delete(`/cart/remove/${cartItemId}`, {
        headers: {
          'User-Id': user.user_id,
          'Role': user.role
        }
      });
      fetchCart();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to remove item');
    }
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    
    if (!selectedAddress) {
      alert('Please add a delivery address in your profile first.');
      navigate('/profile');
      return;
    }
    
    setProcessing(true);
    
    try {
      const response = await api.post(
        '/bookings/',
        {
          delivery_address_id: parseInt(selectedAddress),
          delivery_date: deliveryDate || null,
          mode_of_payment: paymentMode
        },
        {
          headers: {
            'User-Id': user.user_id,
            'Role': user.role
          }
        }
      );
      
      alert(`Order placed successfully! Order ID: ${response.data.booking_id}\nTotal: ₹${response.data.total_price}`);
      setShowCheckout(false);
      fetchCart(); // Refresh cart (should be empty now)
      navigate('/orders');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to place order');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return <div className="cart-page">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <div className="cart-page">
      <h1>Shopping Cart</h1>
      {cartItems.length === 0 ? (
        <div>
          <p>Your cart is empty.</p>
          <Link to="/products" className="btn">
            Continue Shopping
          </Link>
        </div>
      ) : (
        <>
          <table className="cart-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Total</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {cartItems.map(item => (
                <tr key={item.cart_item_id}>
                  <td>{item.product_name}</td>
                  <td>₹{item.price}</td>
                  <td>
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => updateQuantity(item.cart_item_id, parseInt(e.target.value) || 1)}
                      min="1"
                      style={{ width: '60px' }}
                    />
                  </td>
                  <td>₹{item.total_price}</td>
                  <td>
                    <button
                      onClick={() => removeFromCart(item.cart_item_id)}
                      className="btn btn-sm btn-danger"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="cart-summary">
            <h3>Total: ₹{totalPrice}</h3>
            <Link to="/products" className="btn btn-secondary">
              Continue Shopping
            </Link>
            <button onClick={() => setShowCheckout(true)} className="btn btn-primary">
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
      
      {/* Checkout Modal */}
      {showCheckout && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Checkout</h2>
            <form onSubmit={handleCheckout}>
              <div className="form-group">
                <label>Delivery Address:</label>
                {addresses.length === 0 ? (
                  <p className="text-danger">No address found. <Link to="/profile">Add address in profile</Link></p>
                ) : (
                  <select
                    value={selectedAddress}
                    onChange={(e) => setSelectedAddress(e.target.value)}
                    required
                  >
                    <option value="">Select Address</option>
                    {addresses.map(addr => (
                      <option key={addr.id} value={addr.id}>
                        {addr.address_line_1}, {addr.city}, {addr.state} - {addr.pin_code}
                      </option>
                    ))}
                  </select>
                )}
              </div>
              
              <div className="form-group">
                <label>Delivery Date (optional):</label>
                <input
                  type="date"
                  value={deliveryDate}
                  onChange={(e) => setDeliveryDate(e.target.value)}
                />
              </div>
              
              <div className="form-group">
                <label>Payment Mode:</label>
                <select
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value)}
                  required
                >
                  <option value="cash">Cash</option>
                  <option value="credit">Credit (Buy Now, Pay Later)</option>
                </select>
              </div>
              
              <div className="form-group">
                <h3>Total to Pay: ₹{totalPrice}</h3>
              </div>
              
              <div className="form-actions">
                <button type="button" onClick={() => setShowCheckout(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={processing || addresses.length === 0}>
                  {processing ? 'Processing...' : 'Place Order'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
    </>
  );
};

export default CartPage;