import React, { useCallback, useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';
import { resolveProductImage } from '../utils/products';

const ProductList = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('latest');

  const role = user?.role || 'customer';
  const isAdmin = role === 'admin';

  const fetchBrands = useCallback(async () => {
    try {
      const response = await backendApi.get('/products/brands');
      setBrands(response.data.brands || []);
    } catch (err) {
      console.error('Error fetching brands:', err);
    }
  }, []);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams();

      if (searchTerm.trim()) {
        params.set('search', searchTerm.trim());
      }
      if (selectedBrand) {
        params.set('brand', selectedBrand);
      }
      if (minPrice) {
        params.set('min_price', minPrice);
      }
      if (maxPrice) {
        params.set('max_price', maxPrice);
      }
      if (sortBy) {
        params.set('sort', sortBy);
      }
      if (isAdmin) {
        params.set('mine', 'true');
      }

      const url = params.toString() ? `/products/?${params.toString()}` : '/products/';
      const response = await backendApi.get(url);
      setProducts(response.data.products || []);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError(err.response?.data?.message || 'Failed to load products.');
    } finally {
      setLoading(false);
    }
  }, [isAdmin, maxPrice, minPrice, searchTerm, selectedBrand, sortBy]);

  useEffect(() => {
    fetchBrands();
  }, [fetchBrands]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const addToCart = async (productId, quantity) => {
    if (!user) {
      navigate('/login', { state: { from: location } });
      return;
    }

    try {
      await backendApi.post('/cart/add', { product_id: productId, quantity });
      alert('Item added to cart.');
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to add to cart');
    }
  };

  const deleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }

    try {
      await backendApi.delete(`/products/${productId}`);
      setProducts((currentProducts) =>
        currentProducts.filter((product) => product.id !== productId)
      );
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to delete product');
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedBrand('');
    setMinPrice('');
    setMaxPrice('');
    setSortBy('latest');
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="product-list">Loading products...</div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="product-list marketplace-page">
        <div className="page-hero">
          <div>
            <p className="eyebrow">{isAdmin ? 'Seller inventory' : 'Public marketplace'}</p>
            <h1>{isAdmin ? 'Manage Your Products' : 'Shop Fresh Agricultural Supplies'}</h1>
            <p className="page-subtitle">
              {isAdmin
                ? 'Your catalog, stock, and pricing in one place.'
                : 'Browse products by brand, compare prices, and sort by popularity before you sign in.'}
            </p>
          </div>
          {isAdmin ? (
            <Link to="/products/create" className="btn btn-primary">
              Add New Product
            </Link>
          ) : (
            <Link to={user ? '/customer/dashboard' : '/signup'} className="btn btn-secondary">
              {user ? 'Go to dashboard' : 'Create an account'}
            </Link>
          )}
        </div>

        <div className="catalog-toolbar">
          <div className="catalog-search">
            <label htmlFor="product-search">Search</label>
            <input
              id="product-search"
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search by product name or brand"
            />
          </div>

          <div className="catalog-filter">
            <label htmlFor="brand-filter">Brand</label>
            <select
              id="brand-filter"
              value={selectedBrand}
              onChange={(event) => setSelectedBrand(event.target.value)}
            >
              <option value="">All brands</option>
              {brands.map((brand) => (
                <option key={brand.id} value={brand.name}>
                  {brand.name}
                </option>
              ))}
            </select>
          </div>

          <div className="catalog-filter">
            <label htmlFor="min-price">Min price</label>
            <input
              id="min-price"
              type="number"
              min="0"
              value={minPrice}
              onChange={(event) => setMinPrice(event.target.value)}
              placeholder="0"
            />
          </div>

          <div className="catalog-filter">
            <label htmlFor="max-price">Max price</label>
            <input
              id="max-price"
              type="number"
              min="0"
              value={maxPrice}
              onChange={(event) => setMaxPrice(event.target.value)}
              placeholder="1000"
            />
          </div>

          <div className="catalog-filter">
            <label htmlFor="sort-by">Sort</label>
            <select
              id="sort-by"
              value={sortBy}
              onChange={(event) => setSortBy(event.target.value)}
            >
              <option value="latest">Latest</option>
              <option value="a-z">A-Z</option>
              <option value="price_asc">Price: Low to high</option>
              <option value="price_desc">Price: High to low</option>
              <option value="popular">Most popular</option>
            </select>
          </div>

          <button type="button" className="btn btn-secondary toolbar-clear" onClick={clearFilters}>
            Reset
          </button>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="catalog-meta">
          <span>{products.length} product{products.length === 1 ? '' : 's'}</span>
          {!user && <span>Add to cart will prompt login</span>}
        </div>

        {products.length === 0 ? (
          <div className="empty-state">
            <h2>No products match these filters</h2>
            <p>Try a different brand, wider price range, or a shorter search term.</p>
          </div>
        ) : (
          <div className="product-grid">
            {products.map((product) => (
              <article key={product.id} className="product-card product-card-rich">
                <div className="product-image-wrap">
                  <img
                    src={resolveProductImage(product.image_path)}
                    alt={product.name}
                    className="product-image"
                  />
                  <span className={`product-status ${product.expiry_status}`}>
                    {product.expiry_status === 'expiring_soon'
                      ? 'Expiring soon'
                      : product.expiry_status === 'expired'
                        ? 'Expired'
                        : 'In stock'}
                  </span>
                </div>

                <div className="product-card-body">
                  <p className="product-brand">{product.brand || 'AgriFlow Select'}</p>
                  <h3>{product.name}</h3>
                  <p className="product-description">{product.description || 'No description yet.'}</p>

                  <div className="product-meta-row">
                    <span className="price">Rs. {product.price}</span>
                    <span className="quantity">{product.quantity} available</span>
                  </div>

                  <div className="product-meta-row subtle">
                    <span>Popularity: {product.no_of_orders || 0} orders</span>
                    {isAdmin && <span>Seller: {product.seller_name || 'You'}</span>}
                  </div>

                  <div className="product-actions">
                    <Link to={`/products/${product.id}`} className="btn btn-secondary">
                      View details
                    </Link>

                    {isAdmin ? (
                      <>
                        <Link to={`/products/${product.id}/edit`} className="btn">
                          Edit
                        </Link>
                        <button
                          type="button"
                          onClick={() => deleteProduct(product.id)}
                          className="btn btn-danger"
                        >
                          Delete
                        </button>
                      </>
                    ) : (
                      <button
                        type="button"
                        onClick={() => addToCart(product.id, 1)}
                        className="btn"
                        disabled={product.expiry_status === 'expired' || product.quantity <= 0}
                      >
                        {user ? 'Add to cart' : 'Login to add'}
                      </button>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </>
  );
};

export default ProductList;
