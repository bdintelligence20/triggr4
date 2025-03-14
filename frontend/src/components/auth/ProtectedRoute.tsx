import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import useRoleStore from '../../store/roleStore';
import Loading from '../ui/Loading';

interface ProtectedRouteProps {
  requiredRole?: 'user' | 'admin';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ requiredRole = 'user' }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const { role } = useRoleStore();
  
  // Show loading state while checking authentication
  if (isLoading) {
    return <Loading />;
  }
  
  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // Check if user has the required role
  if (requiredRole === 'admin' && role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  
  // Render the child routes
  return <Outlet />;
};

export default ProtectedRoute;
