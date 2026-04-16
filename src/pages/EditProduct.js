import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { resolveProductImage } from '../utils/products';

const EditProduct = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [name, setName] = useState('');
  const [brand, setBrand] = useState('');
  const [description, setDescription] = useState('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [imagePath, setImagePath] = useState('/static/images/product-placeholder.svg');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchProduct();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchProduct = async () => {
    try {
      if (!user || user.role !== 'admin') {
        navigate('/login');
        return;
      }

      const response = await backendApi.get(`/products/${id}`);
      
      const product = response.data.product;
      setName(product.name || '');
      setBrand(product.brand || '');
      setDescription(product.description || '');
      setQuantity(product.quantity || '');
      setPrice(product.price || '');
      setImagePath(product.image_path || '/static/images/product-placeholder.svg');
      
      if (product.expiry_date) {
        const expiry = new Date(product.expiry_date);
        setExpiryDate(expiry.toISOString().split('T')[0]);
      }
    } catch (err) {
      setError('Failed to load product');
    } finally {
      setInitialLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    if (!user || user.role !== 'admin') {
      navigate('/login');
      return;
    }

    try {
      console.log('Updating product with id:', id);
      const productData = {
        name,
        brand,
        description,
        quantity: parseInt(quantity) || 0,
        price: parseFloat(price) || 0,
        image_path: imagePath,
      };
      console.log('Product data:', productData);
      
      if (expiryDate) {
        productData.expiry_date = expiryDate;
      }

      await backendApi.put(`/products/${id}`, productData);
      
      alert('Product updated successfully!');
      navigate('/products');
    } catch (err) {
      console.error('Update error:', err);
      setError(err.response?.data?.message || 'Failed to update product. Error: ' + (err.message || 'Unknown'));
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return <div className="edit-product-page">Loading...</div>;
  }

  return (
    <>
      <Navbar />
      <div className="edit-product-page">
      <div className="container">
        <h2>Edit Product</h2>
        {error && <div className="alert alert-danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Product Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label>Brand</label>
            <input
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              required
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              min="0"
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label>Price (Rs.)</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              min="0"
              step="0.01"
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label>Image Path</label>
            <input
              type="text"
              value={imagePath}
              onChange={(e) => setImagePath(e.target.value)}
              className="form-control"
            />
            <img
              src={resolveProductImage(imagePath)}
              alt="Product preview"
              className="form-image-preview"
            />
          </div>
          <div className="form-group">
            <label>Expiry Date</label>
            <input
              type="date"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
              className="form-control"
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Updating...' : 'Update Product'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/products')}>
            Cancel
          </button>
        </form>
      </div>
    </div>
    </>
  );
};

export default EditProduct;
