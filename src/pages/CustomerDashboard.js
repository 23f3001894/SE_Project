import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const CustomerDashboard = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/', {
        headers: { 'Role': 'customer' }
      });
      setProducts(response.data.products);
    } catch (err) {
      console.error('Error fetching products:', err);
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
      <div className="customer-dashboard">
      <h1>Customer Dashboard</h1>
      <p>Welcome, {user?.name}!</p>
      
      <div className="section">
        <h2>Available Products</h2>
        {products.length === 0 ? (
          <p>No products available.</p>
        ) : (
          <div className="product-grid">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <h3>{product.name}</h3>
                <p>{product.description}</p>
                <p className="price">₹{product.price}</p>
                <p className="quantity">Available: {product.quantity}</p>
                {product.expiry_status === 'expired' && (
                  <p className="expired">Expired</p>
                )}
                {product.expiry_status === 'expiring_soon' && (
                  <p className="expiring">Expires soon!</p>
                )}
                <Link to={`/products/${product.id}`} className="btn">View Details</Link>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="quick-links">
        <Link to="/cart" className="btn">View Cart</Link>
        <Link to="/orders" className="btn">Order History</Link>
        <Link to="/profile" className="btn">My Profile</Link>
      </div>
    </div>
    </>
  );
};

export default CustomerDashboard;