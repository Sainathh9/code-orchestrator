import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import type { AuthContextType } from '../context/AuthContext';

/**
 * Reusable hook to access global user identity state and session triggers.
 *
 * Raises error if used outside an AuthProvider element hierarchy.
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be executed within an AuthProvider subtree.');
  }
  return context;
};
