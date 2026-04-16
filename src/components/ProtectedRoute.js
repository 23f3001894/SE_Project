import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getDashboardPath, isRoleAllowed } from '../utils/auth';

const ProtectedRoute = ({ allowedRoles = [] }) => {
  const location = useLocation();
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return <div className="route-loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!isRoleAllowed(user?.role, allowedRoles)) {
    return <Navigate to={getDashboardPath(user?.role)} replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
