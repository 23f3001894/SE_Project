import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { backendApi } from '../services/api';
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

  const fetchAddresses = useCallback(async () => {
    if (!user) {
      return;
    }

    try {
      const response = await backendApi.get('/addresses/');
      const nextAddresses = response.data.addresses || [];
      setAddresses(nextAddresses);
      if (nextAddresses.length > 0) {
        setSelectedAddress(String(nextAddresses[0].id));
      }
    } catch (err) {
      console.error('Error fetching addresses:', err);
    }
  }, [user]);

  const fetchCart = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      const response = await backendApi.get('/cart/');
      setCartItems(response.data.cart_items || []);
      setTotalPrice(response.data.total_price || 0);
      await fetchAddresses();
    } catch (err) {
      console.error('Error fetching cart:', err);
    } finally {
      setLoading(false);
    }
  }, [fetchAddresses, user]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const updateQuantity = async (cartItemId, quantity) => {
    if (!user) {
      return;
    }

    try {
      await backendApi.put(`/cart/update/${cartItemId}`, { quantity });
      fetchCart();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to update cart');
    }
  };

  const removeFromCart = async (cartItemId) => {
    if (!user || !window.confirm('Remove item from cart?')) {
      return;
    }

    try {
      await backendApi.delete(`/cart/remove/${cartItemId}`);
      fetchCart();
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to remove item');
    }
  };

  const handleCheckout = async (event) => {
    event.preventDefault();

    if (!selectedAddress) {
      alert('Please add a delivery address in your profile first.');
      navigate('/profile');
      return;
    }

    setProcessing(true);

    try {
      const response = await backendApi.post('/bookings/', {
        delivery_address_id: parseInt(selectedAddress, 10),
        delivery_date: deliveryDate || null,
        mode_of_payment: paymentMode
      });

      alert(
        `Order placed successfully! Order ID: ${response.data.booking_id}\nTotal: Rs. ${response.data.total_price}`
      );
      setShowCheckout(false);
      fetchCart();
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
                {cartItems.map((item) => (
                  <tr key={item.cart_item_id}>
                    <td>{item.product_name}</td>
                    <td>Rs. {item.price}</td>
                    <td>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(event) =>
                          updateQuantity(item.cart_item_id, parseInt(event.target.value, 10) || 1)
                        }
                        min="1"
                        style={{ width: '60px' }}
                      />
                    </td>
                    <td>Rs. {item.total_price}</td>
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
              <h3>Total: Rs. {totalPrice}</h3>
              <Link to="/products" className="btn btn-secondary">
                Continue Shopping
              </Link>
              <button onClick={() => setShowCheckout(true)} className="btn btn-primary">
                Proceed to Checkout
              </button>
            </div>
          </>
        )}

        {showCheckout && (
          <div className="modal-overlay">
            <div className="modal">
              <h2>Checkout</h2>
              <form onSubmit={handleCheckout}>
                <div className="form-group">
                  <label>Delivery Address:</label>
                  {addresses.length === 0 ? (
                    <p className="text-danger">
                      No address found. <Link to="/profile">Add address in profile</Link>
                    </p>
                  ) : (
                    <select
                      value={selectedAddress}
                      onChange={(event) => setSelectedAddress(event.target.value)}
                      required
                    >
                      <option value="">Select Address</option>
                      {addresses.map((address) => (
                        <option key={address.id} value={address.id}>
                          {address.address_line_1}, {address.city}, {address.state} - {address.pin_code}
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
                    onChange={(event) => setDeliveryDate(event.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label>Payment Mode:</label>
                  <select
                    value={paymentMode}
                    onChange={(event) => setPaymentMode(event.target.value)}
                    required
                  >
                    <option value="cash">Cash</option>
                    <option value="credit">Credit (Buy Now, Pay Later)</option>
                  </select>
                </div>

                <div className="form-group">
                  <h3>Total to Pay: Rs. {totalPrice}</h3>
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
