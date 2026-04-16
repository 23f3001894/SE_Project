import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { resolveProductImage } from '../utils/products';

const CreateProduct = () => {
  const { user } = useAuth();
  const [name, setName] = useState('');
  const [brand, setBrand] = useState('');
  const [description, setDescription] = useState('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [imagePath, setImagePath] = useState('/static/images/product-placeholder.svg');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    if (!user || user.role !== 'admin') {
      navigate('/login');
      return;
    }

    try {
      const productData = {
        name,
        brand,
        description,
        quantity: parseInt(quantity),
        price: parseFloat(price),
        image_path: imagePath,
      };
      
      if (expiryDate) {
        productData.expiry_date = expiryDate;
      }

      await backendApi.post('/products/', productData);
      
      alert('Product created successfully!');
      navigate('/products');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="create-product-page">
      <div className="container">
        <h2>Add New Product</h2>
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
              placeholder="AgriFlow Select"
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
              placeholder="/static/images/product-placeholder.svg"
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
            {loading ? 'Creating...' : 'Create Product'}
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

export default CreateProduct;
