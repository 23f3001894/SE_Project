import React, { useCallback, useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { backendApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { getDashboardPath } from '../utils/auth';
import { resolveProductImage } from '../utils/products';

const ProductDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState('');

  const fetchProduct = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const [productResponse, reviewsResponse] = await Promise.all([
        backendApi.get(`/products/${id}`),
        backendApi.get(`/reviews/product/${id}`),
      ]);

      setProduct(productResponse.data.product);
      setReviews(reviewsResponse.data.reviews || []);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load product');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchProduct();
  }, [fetchProduct]);

  const addToCart = async () => {
    if (!user) {
      navigate('/login', { state: { from: location } });
      return;
    }

    try {
      await backendApi.post('/cart/add', { product_id: Number(id), quantity });
      alert('Item added to cart.');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to add to cart');
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="product-details">Loading product...</div>
      </>
    );
  }

  if (error || !product) {
    return (
      <>
        <Navbar />
        <div className="product-details">
          <p>{error || 'Product not found'}</p>
          <Link to="/products" className="btn btn-secondary">
            Back to products
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="product-details product-details-page">
        <Link to={user ? getDashboardPath(user.role) : '/products'} className="btn btn-secondary">
          Back
        </Link>

        <div className="product-detail-layout">
          <div className="product-detail-image-panel">
            <img
              src={resolveProductImage(product.image_path)}
              alt={product.name}
              className="product-detail-image"
            />
          </div>

          <div className="product-detail-content">
            <p className="product-brand">{product.brand || 'AgriFlow Select'}</p>
            <h1>{product.name}</h1>
            <p className="product-detail-description">
              {product.description || 'No description provided yet.'}
            </p>

            <div className="detail-pill-row">
              <span className="detail-pill">Rs. {product.price}</span>
              <span className="detail-pill">{product.quantity} units in stock</span>
              <span className="detail-pill">{product.no_of_orders || 0} orders</span>
            </div>

            {product.expiry_date && (
              <p className="detail-copy">
                Expiry date: {new Date(product.expiry_date).toLocaleDateString()}
              </p>
            )}

            {product.seller_name && (
              <p className="detail-copy">Seller: {product.seller_name}</p>
            )}

            {user?.role !== 'admin' && product.expiry_status !== 'expired' && (
              <div className="add-to-cart detail-cart-panel">
                <label htmlFor="detail-quantity">Quantity</label>
                <input
                  id="detail-quantity"
                  type="number"
                  value={quantity}
                  onChange={(event) => setQuantity(parseInt(event.target.value, 10) || 1)}
                  min="1"
                  max={product.quantity}
                />
                <button onClick={addToCart} className="btn">
                  {user ? 'Add to cart' : 'Login to add'}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="section">
          <h2>Customer Reviews</h2>
          {reviews.length === 0 ? (
            <p>No reviews yet for this product.</p>
          ) : (
            <div className="reviews-section">
              {reviews.map((review) => (
                <div key={review.id} className="review-card">
                  <p>
                    <strong>{review.user_name}</strong>
                  </p>
                  <p>Rating: {review.rating}/5</p>
                  <p>{review.review}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ProductDetails;
