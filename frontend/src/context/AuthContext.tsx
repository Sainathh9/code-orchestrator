import React, { createContext, useState, useEffect, type ReactNode } from 'react';
import type { User } from '../types/auth';
import { authApi } from '../api/auth';

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: () => Promise<void>;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  registerWithEmail: (email: string, password: string) => Promise<void>;
  handleCallback: (code: string, state: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // On mount: check if access token exists in localStorage, and retrieve user profile
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
        } catch (error) {
          console.error('Failed to initialize user session:', error);
          // Token expired or invalid, client interceptor will have removed token.
          setUser(null);
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  /**
   * Initiate Google OAuth flow by fetching the redirect login URL and
   * setting the state token inside sessionStorage before navigating.
   */
  const login = async () => {
    try {
      setLoading(true);
      const { auth_url, state } = await authApi.getLoginUrl();
      // Store state CSRF parameter to verify in the callback route later
      sessionStorage.setItem('oauth_state', state);
      window.location.href = auth_url;
    } catch (error) {
      console.error('Error starting login flow:', error);
      setLoading(false);
      throw error;
    }
  };

  /**
   * Complete code exchange callback, persist token, fetch user profile,
   * and update auth state variables.
   */
  const handleCallback = async (code: string, state: string) => {
    try {
      setLoading(true);
      const savedState = sessionStorage.getItem('oauth_state');
      if (savedState && savedState !== state) {
        throw new Error('CSRF State mismatch. Suspicious request rejected.');
      }
      sessionStorage.removeItem('oauth_state');

      const data = await authApi.loginCallback(code, state);
      localStorage.setItem('access_token', data.access_token);

      const profile = await authApi.getMe();
      setUser(profile);
    } catch (error) {
      console.error('Callback OAuth flow failure:', error);
      localStorage.removeItem('access_token');
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Revoke token at backend, purge local credentials, and redirect.
   */
  const logout = async () => {
    try {
      setLoading(true);
      await authApi.logout();
    } catch (error) {
      console.error('Error logging out from server:', error);
    } finally {
      localStorage.removeItem('access_token');
      setUser(null);
      setLoading(false);
    }
  };

  const loginWithEmail = async (email: string, password: string) => {
    try {
      setLoading(true);
      const data = await authApi.emailLogin(email, password);
      localStorage.setItem('access_token', data.access_token);
      const profile = await authApi.getMe();
      setUser(profile);
    } catch (error) {
      console.error('Email authentication failure:', error);
      localStorage.removeItem('access_token');
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const registerWithEmail = async (email: string, password: string) => {
    try {
      setLoading(true);
      const data = await authApi.register(email, password);
      localStorage.setItem('access_token', data.access_token);
      const profile = await authApi.getMe();
      setUser(profile);
    } catch (error) {
      console.error('Email registration failure:', error);
      localStorage.removeItem('access_token');
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    loginWithEmail,
    registerWithEmail,
    handleCallback,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
