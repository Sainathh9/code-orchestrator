import { apiClient } from './client';
import type { User } from '../types/auth';

export interface LoginInitiateResponse {
  auth_url: string;
  state: string;
}

export interface LoginCallbackResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string | null;
    profile_picture: string | null;
  };
}

export const authApi = {
  /**
   * Start Google OAuth flow. Fetch authentication redirect URL and state token.
   */
  async getLoginUrl(): Promise<LoginInitiateResponse> {
    const response = await apiClient.get<LoginInitiateResponse>('/auth/login');
    return response.data;
  },

  /**
   * Complete Google OAuth callback. Exchange code and state token for JWT.
   */
  async loginCallback(code: string, state: string): Promise<LoginCallbackResponse> {
    const response = await apiClient.get<LoginCallbackResponse>('/auth/callback', {
      params: { code, state },
    });
    return response.data;
  },

  /**
   * Fetch currently authenticated user profile.
   */
  async getMe(): Promise<User> {
    const response = await apiClient.get<any>('/auth/me');
    const data = response.data;
    return {
      id: data.id,
      email: data.email,
      name: data.name,
      profilePicture: data.profile_picture,
      createdAt: data.created_at,
    };
  },

  /**
   * Perform direct email login.
   */
  async emailLogin(email: string, password: string): Promise<LoginCallbackResponse> {
    const response = await apiClient.post<LoginCallbackResponse>('/auth/email-login', {
      email,
      password,
    });
    return response.data;
  },

  /**
   * Register a new account with email and password.
   */
  async register(email: string, password: string): Promise<LoginCallbackResponse> {
    const response = await apiClient.post<LoginCallbackResponse>('/auth/register', {
      email,
      password,
    });
    return response.data;
  },

  /**
   * Perform logout: revoke JWT by adding to Redis deny-list.
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
  },
};
