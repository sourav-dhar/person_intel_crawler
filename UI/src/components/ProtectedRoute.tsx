import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../hooks/redux';

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const location = useLocation();
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  
  // Check if authentication is enabled in the environment
  const authEnabled = import.meta.env.VITE_AUTH_ENABLED === 'true';
  
  // If auth is disabled, just render the children
  if (!authEnabled) {
    return <>{children}</>;
  }
  
  // If auth is enabled and user is authenticated, render the children
  if (isAuthenticated) {
    return <>{children}</>;
  }
  
  // Otherwise, redirect to login
  return <Navigate to="/login" state={{ from: location }} replace />;
};

export default ProtectedRoute;