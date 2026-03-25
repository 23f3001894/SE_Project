import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';

const ProductList = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState(user?.role || 'customer');

  useEffect(() => {
    if (user) {
      setRole(user.role);
    }
    fetchProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/', {
        headers: { 'Role': role }
      });
      setProducts(response.data.products);
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId, quantity) => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
      alert('Please log in');
      return;
    }
    try {
      await api.post(
        '/cart/add',
        { product_id: productId, quantity },
        {
          headers: {
            'User-ID': user.id,
            'Role': user.role
          }
        }
      );
      alert('Item added to cart');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to add to cart');
    }
  };

  const deleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }
    try {
      await api.delete(`/products/${productId}`, {
        headers: { 'Role': 'admin' }
      });
      // Remove from list
      setProducts(prev => prev.filter(p => p.id !== productId));
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete product');
    }
  };

  if (loading) {
    return <div className="product-list">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <div className="product-list">
      <h1>Products</h1>
      {role === 'admin' && (
        <Link to="/products/create" className="btn mb-4">
          Add New Product
        </Link>
      )}
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
            {role === 'customer' && product.expiry_status !== 'expired' && (
              <>
                <button
                  onClick={() => addToCart(product.id, 1)}
                  className="btn btn-sm"
                >
                  Add to Cart
                </button>
                <Link to={`/products/${product.id}`} className="btn btn-sm">
                  Details
                </Link>
              </>
            )}
            {role === 'admin' && (
              <div className="admin-actions">
                <Link to={`/products/${product.id}/edit`} className="btn btn-sm">
                  Edit
                </Link>
                <button
                  onClick={() => deleteProduct(product.id)}
                  className="btn btn-sm btn-danger"
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
    </>
  );
};

export default ProductList;
