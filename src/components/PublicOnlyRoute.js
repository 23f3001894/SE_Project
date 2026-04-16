import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getDashboardPath } from '../utils/auth';

const PublicOnlyRoute = () => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return <div className="route-loading">Loading...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to={getDashboardPath(user?.role)} replace />;
  }

  return <Outlet />;
};

export default PublicOnlyRoute;
