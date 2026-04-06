import { create } from "zustand";
import type { User } from "@/types";

// CSRF token stored in memory (not localStorage for better security)
const CSRF_STORAGE_KEY = "boardy_csrf";

interface AuthState {
  user: User | null;
  csrfToken: string | null;
  setAuth: (user: User, csrfToken: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  getCsrfToken: () => string | null;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  // Initialize from sessionStorage (survives refresh, cleared on tab close)
  csrfToken: sessionStorage.getItem(CSRF_STORAGE_KEY),

  setAuth: (user, csrfToken) => {
    // Store CSRF token in sessionStorage (not localStorage)
    sessionStorage.setItem(CSRF_STORAGE_KEY, csrfToken);
    set({ user, csrfToken });
  },

  logout: () => {
    sessionStorage.removeItem(CSRF_STORAGE_KEY);
    set({ user: null, csrfToken: null });
  },

  isAuthenticated: () => !!get().user || !!get().csrfToken,

  getCsrfToken: () => get().csrfToken,
}));
