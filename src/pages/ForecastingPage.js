import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import Navbar from '../components/Navbar';

const ForecastingPage = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [forecastMonths, setForecastMonths] = useState(3);
  const [forecast, setForecast] = useState(null);
  const [highDemandProducts, setHighDemandProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [forecastLoading, setForecastLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch products for dropdown
      const productsRes = await api.get('/products/', {
        headers: { 'Role': 'admin' }
      });
      setProducts(productsRes.data.products || []);
      
      // Fetch high demand recommendations
      const demandRes = await api.get('/admin/recommendations/high-demand', {
        headers: { 'Role': 'admin' }
      });
      setHighDemandProducts(demandRes.data.high_demand_recommendations || []);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleForecast = async (e) => {
    e.preventDefault();
    if (!selectedProduct) return;
    
    setForecastLoading(true);
    try {
      const response = await api.get(
        `/admin/forecast/demand?product_id=${selectedProduct}&months_ahead=${forecastMonths}`,
        { headers: { 'Role': 'admin' } }
      );
      setForecast(response.data);
    } catch (err) {
      console.error('Error fetching forecast:', err);
      alert('Failed to get forecast. Make sure the product has sales data.');
    } finally {
      setForecastLoading(false);
    }
  };

  if (loading) {
    return <><Navbar /><div className="forecasting-page">Loading...</div></>;
  }

  return (
    <>
      <Navbar />
      <div className="forecasting-page">
      <h1>Demand Forecasting & Analytics</h1>
      
      {/* Demand Forecast Section */}
      <div className="section">
        <h2>📊 Demand Forecast</h2>
        <p>Predict future demand based on historical sales trends</p>
        
        <form onSubmit={handleForecast} className="forecast-form">
          <div className="form-group">
            <label>Select Product:</label>
            <select 
              value={selectedProduct} 
              onChange={(e) => setSelectedProduct(e.target.value)}
              required
            >
              <option value="">-- Select a Product --</option>
              {products.map(product => (
                <option key={product.id} value={product.id}>
                  {product.name} (Current Stock: {product.quantity})
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Forecast Period (months):</label>
            <select 
              value={forecastMonths} 
              onChange={(e) => setForecastMonths(parseInt(e.target.value))}
            >
              <option value="1">1 Month</option>
              <option value="3">3 Months</option>
              <option value="6">6 Months</option>
              <option value="12">12 Months</option>
            </select>
          </div>
          
          <button type="submit" className="btn" disabled={forecastLoading}>
            {forecastLoading ? 'Analyzing...' : 'Generate Forecast'}
          </button>
        </form>
        
        {forecast && (
          <div className="forecast-results">
            <h3>Forecast for {forecast.product_name}</h3>
            <p><strong>Method:</strong> {forecast.method}</p>
            <p><strong>Historical Data Points:</strong> {forecast.historical_data_points}</p>
            
            <table className="forecast-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Predicted Demand</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {forecast.forecast.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.month}/{item.year}</td>
                    <td>{item.predicted_quantity} units</td>
                    <td>
                      <span className={`confidence ${item.confidence || 'medium'}`}>
                        {item.confidence || 'medium'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* High Demand Recommendations */}
      <div className="section">
        <h2>🔥 High Demand Products</h2>
        <p>Products that are currently in high demand based on recent sales</p>
        
        {highDemandProducts.length === 0 ? (
          <p>No high demand data available yet. Sales data will accumulate over time.</p>
        ) : (
          <div className="recommendations-grid">
            {highDemandProducts.map(product => (
              <div key={product.product_id} className="recommendation-card">
                <h3>{product.product_name}</h3>
                <p><strong>Units Sold (30 days):</strong> {product.units_sold_last_30_days}</p>
                <p><strong>Demand Level:</strong> 
                  <span className={`demand-badge ${product.demand_level}`}>
                    {product.demand_level.toUpperCase()}
                  </span>
                </p>
                <p className="recommendation-action">{product.recommended_action}</p>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Push Expiry Products */}
      <div className="section">
        <h2>⚠️ Push Expiry Products</h2>
        <p>Products nearing expiry that should be prioritized for sale</p>
        
        {products.filter(p => p.expiry_status === 'expiring_soon' || p.expiry_status === 'expired').length === 0 ? (
          <p>No expiring products.</p>
        ) : (
          <div className="recommendations-grid">
            {products.filter(p => p.expiry_status === 'expiring_soon' || p.expiry_status === 'expired').map(product => (
              <div key={product.id} className={`recommendation-card ${product.expiry_status === 'expired' ? 'expired' : 'expiring'}`}>
                <h3>{product.name}</h3>
                <p><strong>Current Stock:</strong> {product.quantity} units</p>
                <p><strong>Status:</strong> 
                  <span className={`demand-badge ${product.expiry_status === 'expired' ? 'expired' : 'expiring'}`}>
                    {product.expiry_status === 'expired' ? 'EXPIRED' : 'EXPIRING SOON'}
                  </span>
                </p>
                {product.expiry_date && (
                  <p><strong>Expiry Date:</strong> {new Date(product.expiry_date).toLocaleDateString()}</p>
                )}
                <p className="recommendation-action">
                  {product.expiry_status === 'expired' 
                    ? 'Remove from inventory - cannot be sold'
                    : 'Discount and push sales to avoid loss'}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
      </div>
    </>
  );
};

export default ForecastingPage;
