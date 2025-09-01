import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ requireAdmin = false }) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check if admin access is required
  if (requireAdmin && !user?.is_admin) {
    return <Navigate to="/unauthorized" replace />;
  }

  // User is authenticated and has required permissions
  return <Outlet />;
};

export default ProtectedRoute;