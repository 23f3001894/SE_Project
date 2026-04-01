import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';

const ProductDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProduct();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchProduct = async () => {
    try {
      const role = user?.role || 'customer';
      const response = await api.get(`/products/${id}`, {
        headers: { 'Role': role }
      });
      setProduct(response.data.product);
      
      // Fetch reviews for this product
      const reviewsRes = await api.get(`/reviews/product/${id}`, {
        headers: { 'Role': role }
      });
      setReviews(reviewsRes.data.reviews || []);
    } catch (err) {
      setError('Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async () => {
    if (!user) {
      alert('Please log in to add to cart');
      navigate('/login');
      return;
    }
    
    try {
      await api.post(
        '/cart/add',
        { product_id: id, quantity },
        {
          headers: {
            'User-Id': user.user_id,
            'Role': user.role
          }
        }
      );
      alert('Item added to cart!');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to add to cart');
    }
  };

  if (loading) {
    return <><Navbar /><div className="product-details">Loading...</div></>;
  }

  if (error) {
    return <><Navbar /><div className="product-details">{error}</div></>;
  }

  if (!product) {
    return <><Navbar /><div className="product-details">Product not found</div></>;
  }

  return (
    <>
      <Navbar />
      <div className="product-details">
        <Link to="/customer/dashboard" className="btn">Back to Dashboard</Link>
      
      <div className="product-info">
        <h2>{product.name}</h2>
        <p className="description">{product.description}</p>
        <p className="price">Price: ₹{product.price}</p>
        <p className="quantity">Available: {product.quantity} units</p>
        
        {product.expiry_status === 'expired' && (
          <p className="expired">This product has expired</p>
        )}
        {product.expiry_status === 'expiring_soon' && (
          <p className="expiring">This product is expiring soon!</p>
        )}
        {product.expiry_date && (
          <p className="expiry">Expiry Date: {new Date(product.expiry_date).toLocaleDateString()}</p>
        )}
      </div>

      {user?.role === 'customer' && product.expiry_status !== 'expired' && (
        <div className="add-to-cart">
          <label>
            Quantity:
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              min="1"
              max={product.quantity}
            />
          </label>
          <button onClick={addToCart} className="btn">Add to Cart</button>
        </div>
      )}

      {reviews.length > 0 && (
        <div className="reviews-section">
          <h3>Reviews</h3>
          {reviews.map(review => (
            <div key={review.id} className="review">
              <p><strong>{review.user_name}</strong> - {'★'.repeat(review.rating)}{'☆'.repeat(5-review.rating)}</p>
              <p>{review.review}</p>
            </div>
          ))}
        </div>
      )}
      </div>
    </>
  );
};

export default ProductDetails;