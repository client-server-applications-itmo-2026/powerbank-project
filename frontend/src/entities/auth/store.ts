import { create } from 'zustand';
import {
  saveCredentials,
  loadCredentials,
  clearCredentials,
  makeBasicAuthHeader,
} from '../../shared/auth_lib/basicAuth';
import { usersApi } from '../../shared/api/users';
import type { UserRetrieveResponse } from '../../shared/types/api';

interface AuthState {
  user: UserRetrieveResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  restoreSession: () => Promise<void>;
  setUser: (user: UserRetrieveResponse | null) => void;
}

// If credentials exist in localStorage, start in loading state so ProtectedRoute
// waits instead of immediately redirecting to /login before restoreSession runs.
const hasSavedCreds = loadCredentials() !== null;

export const useAuthStore = create<AuthState>((callback) => ({
  user: null,
  isAuthenticated: false,
  isLoading: hasSavedCreds,

  login: async (email: string, password: string) => {
    callback({ isLoading: true });
    try {
      // Temporarily save credentials so apiClient can use them
      saveCredentials({ email, password });
      const user = await usersApi.getMe();
      callback({ user, isAuthenticated: true, isLoading: false });
    } catch (err) {
      clearCredentials();
      callback({ isLoading: false });
      throw err;
    }
  },

  logout: () => {
    clearCredentials();
    callback({ user: null, isAuthenticated: false });
  },

  restoreSession: async () => {
    const creds = loadCredentials();
    if (!creds) return;
    callback({ isLoading: true });
    try {
      const user = await usersApi.getMe();
      callback({ user, isAuthenticated: true, isLoading: false });
    } catch {
      // Stored credentials may be invalid — clean up silently
      clearCredentials();
      callback({ isLoading: false });
    }
  },

  setUser: (user) => callback({ user }),
}));

// Export helper for non-hook contexts (e.g. api client doesn't need it, 
// but kept for potential use)
export { makeBasicAuthHeader };
