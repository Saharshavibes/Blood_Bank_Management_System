import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import apiClient, { AUTH_UNAUTHORIZED_EVENT } from "@/lib/api";
import { sessionStore } from "@/lib/session";
import type {
  AuthUser,
  DonorRegisterPayload,
  HospitalRegisterPayload,
  LoginPayload,
  TokenResponse,
} from "@/types/auth";

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
  registerDonor: (payload: DonorRegisterPayload) => Promise<void>;
  registerHospital: (payload: HospitalRegisterPayload) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  const logout = useCallback(() => {
    const activeSession = sessionStore.getSession();
    if (activeSession?.refreshToken) {
      void apiClient.post("/auth/logout", {
        refresh_token: activeSession.refreshToken,
      }).catch(() => undefined);
    }
    sessionStore.clear();
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
  }, [logout]);

  useEffect(() => {
    const bootstrap = async () => {
      const savedSession = sessionStore.getSession();
      if (!savedSession) {
        setIsBootstrapping(false);
        return;
      }

      setToken(sessionStore.getAccessToken());
      try {
        const { data } = await apiClient.get<AuthUser>("/auth/me");
        setUser(data);
        setToken(sessionStore.getAccessToken());
      } catch {
        logout();
      } finally {
        setIsBootstrapping(false);
      }
    };

    void bootstrap();
  }, [logout]);

  const login = useCallback(async (payload: LoginPayload) => {
    const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
    if (typeof data.token_type !== "string" || data.token_type.toLowerCase() !== "bearer") {
      throw new Error("Unsupported token type returned by auth service.");
    }
    sessionStore.setSession({
      accessToken: data.access_token,
      expiresAt: data.expires_at,
      refreshToken: data.refresh_token,
      refreshExpiresAt: data.refresh_expires_at,
    });
    setToken(data.access_token);
    setUser(data.user);
  }, []);

  const registerDonor = useCallback(async (payload: DonorRegisterPayload) => {
    await apiClient.post("/auth/register/donor", payload);
  }, []);

  const registerHospital = useCallback(async (payload: HospitalRegisterPayload) => {
    await apiClient.post("/auth/register/hospital", payload);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isBootstrapping,
      login,
      logout,
      registerDonor,
      registerHospital,
    }),
    [isBootstrapping, login, logout, registerDonor, registerHospital, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
