import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const LoginPage = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('customer');
  const [mobileNo, setMobileNo] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      }, {
        headers: {
          'Role': role
        }
      });
      const { user_id, role: userRole, name } = response.data;
      login({ user_id, role: userRole, name, email });
      if (userRole === 'admin') {
        console.log('Navigating to admin dashboard...');
        navigate('/admin/dashboard');
      } else {
        console.log('Navigating to customer dashboard...');
        navigate('/customer/dashboard');
      }
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
      const response = await api.post('/auth/register', {
        name,
        email,
        password,
        mobile_no: mobileNo,
        role
      });
      alert(response.data.message || 'Registration successful! Please login.');
      setIsRegistering(false);
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>{isRegistering ? 'AgriFlow Register' : 'AgriFlow Login'}</h2>
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
              Don't have an account?{' '}
              <button type="button" className="btn-link" onClick={() => setIsRegistering(true)}>
                Register here
              </button>
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
              <label>Register as</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="form-control"
              >
                <option value="customer">Customer (Farmer/Retail)</option>
                <option value="admin">Admin (Shop Owner)</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>
            <p className="mt-3">
              Already have an account?{' '}
              <button type="button" className="btn-link" onClick={() => setIsRegistering(false)}>
                Login here
              </button>
            </p>
          </form>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
