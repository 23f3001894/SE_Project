import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';
import { resolvePostLoginPath } from '../utils/auth';

const LoginPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isRegistering = location.pathname === '/signup';
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('customer');
  const [mobileNo, setMobileNo] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  useEffect(() => {
    setError('');
  }, [isRegistering]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await authApi.post('/auth/login', { email, password });
      login(response.data);

      const destination = resolvePostLoginPath(
        response.data.role,
        location.state?.from
      );
      navigate(destination, { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await authApi.post('/auth/register', {
        name,
        email,
        password,
        mobile_no: mobileNo,
        role
      });
      login(response.data);
      navigate(resolvePostLoginPath(response.data.role), { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-layout">
        <div className="login-intro">
          <p className="eyebrow">AgriFlow marketplace</p>
          <h1>Modern commerce for growers, buyers, and sellers.</h1>
          <p className="page-subtitle">
            Discover agricultural products without logging in, then move from cart to delivery with a cleaner, production-style flow.
          </p>
          <div className="login-highlight-grid">
            <div className="login-highlight-card">
              <strong>Customer flow</strong>
              <span>Browse, filter, order, and track deliveries.</span>
            </div>
            <div className="login-highlight-card">
              <strong>Seller flow</strong>
              <span>Manage products, forecasting, and order fulfillment.</span>
            </div>
          </div>
        </div>

        <div className="login-container">
          <h2>{isRegistering ? 'Create your AgriFlow account' : 'Sign in to AgriFlow'}</h2>
          {error && <div className="alert alert-danger">{error}</div>}

          {!isRegistering ? (
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="form-control"
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
              </button>
              <p className="mt-3">
                Don't have an account? <Link to="/signup" className="btn-link">Register here</Link>
              </p>
              <p className="mt-3">
                Prefer to browse first? <Link to="/products" className="btn-link">Explore products</Link>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Mobile No</label>
                <input
                  type="text"
                  value={mobileNo}
                  onChange={(e) => setMobileNo(e.target.value)}
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>I am joining AgriFlow as</label>
                <div className="role-options">
                  <label className="role-option">
                    <input
                      type="radio"
                      name="role"
                      value="customer"
                      checked={role === 'customer'}
                      onChange={(e) => setRole(e.target.value)}
                    />
                    <span>Customer buying products</span>
                  </label>
                  <label className="role-option">
                    <input
                      type="radio"
                      name="role"
                      value="admin"
                      checked={role === 'admin'}
                      onChange={(e) => setRole(e.target.value)}
                    />
                    <span>Seller managing products</span>
                  </label>
                </div>
              </div>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Registering...' : 'Register'}
              </button>
              <p className="mt-3">
                Already have an account? <Link to="/login" className="btn-link">Login here</Link>
              </p>
              <p className="mt-3">
                Want to browse before signing up? <Link to="/products" className="btn-link">View the marketplace</Link>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
