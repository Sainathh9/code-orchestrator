import axios from 'axios';

// Vite environments can override this by defining VITE_API_URL in .env
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: inject the JWT access token into the Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: handle token expiration / global API failures
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If we receive a 401 Unauthorized, it means our session token expired or is invalid.
    // We clean up localStorage and redirect to login page.
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      // Prevent infinite redirect loops if we are already on the login route
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = `/login?expired=true&redirect=${encodeURIComponent(
          window.location.pathname
        )}`;
      }
    }
    return Promise.reject(error);
  }
);
