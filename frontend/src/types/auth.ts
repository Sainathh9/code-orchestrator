export interface User {
  id: string;
  email: string;
  name: string | null;
  profilePicture: string | null;
  createdAt?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
}
