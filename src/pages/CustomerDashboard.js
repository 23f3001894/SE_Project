import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';
import { resolveProductImage } from '../utils/products';

const CustomerDashboard = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await backendApi.get('/products/?sort=popular');
      setProducts((response.data.products || []).slice(0, 4));
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
          <h2>Popular Right Now</h2>
          {products.length === 0 ? (
            <p>No products available.</p>
          ) : (
            <div className="product-grid">
              {products.map((product) => (
                <div key={product.id} className="product-card">
                  <img
                    src={resolveProductImage(product.image_path)}
                    alt={product.name}
                    className="product-image"
                  />
                  <p className="product-brand">{product.brand}</p>
                  <h3>{product.name}</h3>
                  <p>{product.description}</p>
                  <p className="price">Rs. {product.price}</p>
                  <p className="quantity">Available: {product.quantity}</p>
                  {product.expiry_status === 'expired' && (
                    <p className="expired">Expired</p>
                  )}
                  {product.expiry_status === 'expiring_soon' && (
                    <p className="expiring">Expires soon!</p>
                  )}
                  <Link to={`/products/${product.id}`} className="btn">
                    View Details
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="quick-links">
          <Link to="/products" className="btn">Browse Full Catalog</Link>
          <Link to="/cart" className="btn">View Cart</Link>
          <Link to="/orders" className="btn">Order History</Link>
          <Link to="/profile" className="btn">My Profile</Link>
        </div>
      </div>
    </>
  );
};

export default CustomerDashboard;
