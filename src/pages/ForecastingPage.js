import React, { useCallback, useEffect, useState } from 'react';
import { backendApi } from '../services/api';
import Navbar from '../components/Navbar';

const ForecastingPage = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [forecastMonths, setForecastMonths] = useState(3);
  const [forecast, setForecast] = useState(null);
  const [highDemandProducts, setHighDemandProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [forecastLoading, setForecastLoading] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [productsRes, demandRes] = await Promise.all([
        backendApi.get('/products/?mine=true&sort=popular'),
        backendApi.get('/admin/recommendations/high-demand'),
      ]);
      setProducts(productsRes.data.products || []);
      setHighDemandProducts(demandRes.data.high_demand_recommendations || []);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleForecast = async (event) => {
    event.preventDefault();
    if (!selectedProduct) {
      return;
    }

    setForecastLoading(true);
    try {
      const response = await backendApi.get(
        `/admin/forecast-demand/${selectedProduct}?months_ahead=${forecastMonths}`
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
    return (
      <>
        <Navbar />
        <div className="forecasting-page">Loading...</div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="forecasting-page marketplace-page">
        <section className="page-hero">
          <div>
            <p className="eyebrow">Demand intelligence</p>
            <h1>Forecast product demand</h1>
            <p className="page-subtitle">
              Use recent order history to estimate upcoming demand and decide where to push inventory.
            </p>
          </div>
        </section>

        <div className="section">
          <h2>Demand Forecast</h2>
          <p>Predict future demand using a moving-average forecast based on your order history.</p>

          <form onSubmit={handleForecast} className="forecast-form">
            <div className="form-group">
              <label>Select Product</label>
              <select value={selectedProduct} onChange={(event) => setSelectedProduct(event.target.value)} required>
                <option value="">Select a product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} | stock {product.quantity}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Forecast Period</label>
              <select value={forecastMonths} onChange={(event) => setForecastMonths(parseInt(event.target.value, 10))}>
                <option value="1">1 month</option>
                <option value="3">3 months</option>
                <option value="6">6 months</option>
                <option value="12">12 months</option>
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
                  {forecast.forecast.map((item, index) => (
                    <tr key={`${item.month}-${item.year}-${index}`}>
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

        <div className="dashboard-grid">
          <div className="section dashboard-panel">
            <h2>High Demand Products</h2>
            {highDemandProducts.length === 0 ? (
              <p>No high demand data available yet.</p>
            ) : (
              <div className="recommendations-grid">
                {highDemandProducts.map((product) => (
                  <div key={product.product_id} className="recommendation-card">
                    <h3>{product.product_name}</h3>
                    <p><strong>Units Sold (30 days):</strong> {product.units_sold_last_30_days}</p>
                    <p>
                      <strong>Demand Level:</strong>
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

          <div className="section dashboard-panel">
            <h2>Push Expiry Products</h2>
            {products.filter((product) => product.expiry_status === 'expiring_soon' || product.expiry_status === 'expired').length === 0 ? (
              <p>No expiring products.</p>
            ) : (
              <div className="recommendations-grid">
                {products
                  .filter((product) => product.expiry_status === 'expiring_soon' || product.expiry_status === 'expired')
                  .map((product) => (
                    <div key={product.id} className={`recommendation-card ${product.expiry_status === 'expired' ? 'expired' : 'expiring'}`}>
                      <h3>{product.name}</h3>
                      <p><strong>Current Stock:</strong> {product.quantity} units</p>
                      <p>
                        <strong>Status:</strong>
                        <span className={`demand-badge ${product.expiry_status === 'expired' ? 'expired' : 'expiring'}`}>
                          {product.expiry_status === 'expired' ? 'EXPIRED' : 'EXPIRING SOON'}
                        </span>
                      </p>
                      {product.expiry_date && (
                        <p><strong>Expiry Date:</strong> {new Date(product.expiry_date).toLocaleDateString()}</p>
                      )}
                      <p className="recommendation-action">
                        {product.expiry_status === 'expired'
                          ? 'Remove from inventory because it can no longer be sold.'
                          : 'Feature it in promotions and move stock before it becomes a loss.'}
                      </p>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default ForecastingPage;
