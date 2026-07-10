import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppRoutes } from './routes/AppRoutes';

/**
 * Root Application Component.
 *
 * Configures the single-page application wrappers:
 *   1. BrowserRouter: Coordinates routing history and route resolution.
 *   2. AuthProvider: Provides global reactive auth state and actions context.
 *   3. AppRoutes: Mounts the main navigation table of routes.
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
