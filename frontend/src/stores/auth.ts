import { create } from "zustand";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("boardy_token"),

  setAuth: (user, token) => {
    localStorage.setItem("boardy_token", token);
    set({ user, token });
  },

  logout: () => {
    localStorage.removeItem("boardy_token");
    set({ user: null, token: null });
  },

  isAuthenticated: () => !!get().token,
}));
