import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const isAdmin = user.role === 'admin';

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to={isAdmin ? "/admin/dashboard" : "/customer/dashboard"}>
          AgriFlow
        </Link>
      </div>
      
      <div className="navbar-links">
        {isAdmin ? (
          // Admin Navigation
          <>
            <Link to="/admin/dashboard">Dashboard</Link>
            <Link to="/products">Products</Link>
            <Link to="/orders">Orders</Link>
            <Link to="/forecasting">Forecasting</Link>
          </>
        ) : (
          // Customer Navigation
          <>
            <Link to="/customer/dashboard">Dashboard</Link>
            <Link to="/products">Products</Link>
            <Link to="/cart">Cart</Link>
            <Link to="/orders">Orders</Link>
            <Link to="/profile">Profile</Link>
          </>
        )}
      </div>

      <div className="navbar-user">
        <span>Welcome, {user.name}</span>
        <button onClick={handleLogout} className="btn-logout">
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;