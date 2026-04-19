import axios from "axios";

import { sessionStore } from "@/lib/session";
import type { TokenResponse } from "@/types/auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
export const AUTH_UNAUTHORIZED_EVENT = "bbms:auth-unauthorized";

const AUTH_PATH_SEGMENTS = [
  "/auth/login",
  "/auth/refresh",
  "/auth/logout",
  "/auth/logout-all",
  "/auth/register",
];

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

let refreshInFlight: Promise<string | null> | null = null;

function isAuthRequest(url: string | undefined): boolean {
  if (!url) {
    return false;
  }
  return AUTH_PATH_SEGMENTS.some((segment) => url.includes(segment));
}

function emitUnauthorizedEvent(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
}

async function rotateSessionIfPossible(): Promise<string | null> {
  const refreshToken = sessionStore.getRefreshToken();
  if (!refreshToken) {
    sessionStore.clear();
    return null;
  }

  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const { data } = await refreshClient.post<TokenResponse>("/auth/refresh", {
          refresh_token: refreshToken,
        });

        if (typeof data.token_type !== "string" || data.token_type.toLowerCase() !== "bearer") {
          sessionStore.clear();
          return null;
        }

        sessionStore.setSession({
          accessToken: data.access_token,
          expiresAt: data.expires_at,
          refreshToken: data.refresh_token,
          refreshExpiresAt: data.refresh_expires_at,
        });
        return data.access_token;
      } catch {
        sessionStore.clear();
        return null;
      } finally {
        refreshInFlight = null;
      }
    })();
  }

  return refreshInFlight;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

apiClient.interceptors.request.use(async (config) => {
  let token = sessionStore.getAccessToken();

  if (!token && !isAuthRequest(config.url)) {
    token = await rotateSessionIfPossible();
    if (!token) {
      emitUnauthorizedEvent();
    }
  }

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const originalRequest = error.config as (typeof error.config & { _authRetried?: boolean }) | undefined;

      if (originalRequest && !originalRequest._authRetried && !isAuthRequest(originalRequest.url)) {
        originalRequest._authRetried = true;
        const refreshedToken = await rotateSessionIfPossible();
        if (refreshedToken) {
          originalRequest.headers = originalRequest.headers ?? {};
          originalRequest.headers.Authorization = `Bearer ${refreshedToken}`;
          return apiClient.request(originalRequest);
        }
      }

      sessionStore.clear();
      emitUnauthorizedEvent();
    }
    return Promise.reject(error);
  },
);

export default apiClient;
