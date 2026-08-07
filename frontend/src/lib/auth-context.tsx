"use client";

/**
 * Auth Context — manages JWT tokens + user state.
 *
 * Remember me: tokens stored in localStorage (persist across sessions).
 * On mount: checks localStorage for existing token → auto-login.
 * On token expiry: uses refresh token to get new access token.
 */

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

interface AuthUser {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  role: string;
}

interface AuthContextType {
  user: AuthUser | null;
  accessToken: string | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  accessToken: null,
  isLoading: true,
  isLoggedIn: false,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user profile with token
  const fetchUser = useCallback(async (token: string): Promise<AuthUser | null> => {
    try {
      const res = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {}
    return null;
  }, []);

  // Try to refresh the access token
  const tryRefresh = useCallback(async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem("refresh_token") || sessionStorage.getItem("refresh_token");
    if (!refreshToken) return null;

    try {
      const res = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (res.ok) {
        const data = await res.json();
        return data.access_token;
      }
    } catch {}

    // Refresh failed — clear everything
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    return null;
  }, []);

  // On mount: restore session from localStorage or sessionStorage
  useEffect(() => {
    const restore = async () => {
      // Check both storages
      let token = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");

      if (token) {
        const userData = await fetchUser(token);
        if (userData) {
          setAccessToken(token);
          setUser(userData);
          setIsLoading(false);
          return;
        }

        // Token expired — try refresh
        token = await tryRefresh();
        if (token) {
          const persist = localStorage.getItem("auth_persist") || "local";
          const storage = persist === "session" ? sessionStorage : localStorage;
          storage.setItem("access_token", token);
          const userData = await fetchUser(token);
          if (userData) {
            setAccessToken(token);
            setUser(userData);
            setIsLoading(false);
            return;
          }
        }
      }

      setIsLoading(false);
    };

    restore();
  }, [fetchUser, tryRefresh]);

  const login = useCallback((newAccessToken: string, newRefreshToken: string) => {
    // Check if user chose "remember me" (default: localStorage)
    const persist = localStorage.getItem("auth_persist") || "local";
    const storage = persist === "session" ? sessionStorage : localStorage;

    storage.setItem("access_token", newAccessToken);
    storage.setItem("refresh_token", newRefreshToken);
    setAccessToken(newAccessToken);

    // Fetch user in background
    fetchUser(newAccessToken).then((userData) => {
      if (userData) setUser(userData);
    });
  }, [fetchUser]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("auth_persist");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    setAccessToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        isLoading,
        isLoggedIn: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
