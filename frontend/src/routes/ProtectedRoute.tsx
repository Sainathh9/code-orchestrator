import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Route guard wrapper preventing unauthorized access.
 *
 * Displays a loading placeholder while checking token validity.
 * Redirects to `/login` with referral parameters on unauthenticated sessions.
 */
export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          fontFamily: 'Inter, sans-serif',
          background: '#0d1117',
          color: '#c9d1d9',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              border: '4px solid #30363d',
              borderTop: '4px solid #58a6ff',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 16px',
            }}
          />
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
          <div>Initializing Secure Session...</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page, preserving target path for redirection after successful auth callback
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};
