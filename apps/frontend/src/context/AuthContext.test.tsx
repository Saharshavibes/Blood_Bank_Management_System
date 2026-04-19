import { act, render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";

const apiMocks = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

const sessionStoreMocks = vi.hoisted(() => ({
  getSession: vi.fn(),
  getAccessToken: vi.fn(),
  setSession: vi.fn(),
  clear: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  AUTH_UNAUTHORIZED_EVENT: "bbms:auth-unauthorized",
  default: {
    get: apiMocks.get,
    post: apiMocks.post,
  },
}));

vi.mock("@/lib/session", () => ({
  sessionStore: sessionStoreMocks,
}));

import { AuthProvider, useAuth } from "@/context/AuthContext";
import { AUTH_UNAUTHORIZED_EVENT } from "@/lib/api";

function AuthProbe() {
  const { user, token, isAuthenticated, isBootstrapping } = useAuth();

  return (
    <div>
      <div data-testid="bootstrapping">{isBootstrapping ? "yes" : "no"}</div>
      <div data-testid="authenticated">{isAuthenticated ? "yes" : "no"}</div>
      <div data-testid="user">{user?.email ?? "none"}</div>
      <div data-testid="token">{token ?? "none"}</div>
    </div>
  );
}

describe("AuthProvider", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStoreMocks.getSession.mockReturnValue(null);
    sessionStoreMocks.getAccessToken.mockReturnValue(null);
    apiMocks.post.mockResolvedValue({});
  });

  it("clears active session when unauthorized event is emitted", async () => {
    sessionStoreMocks.getSession.mockReturnValue({
      accessToken: "access-token",
      expiresAt: "2099-01-01T00:00:00.000Z",
      refreshToken: "refresh-token",
      refreshExpiresAt: "2099-01-02T00:00:00.000Z",
    });
    sessionStoreMocks.getAccessToken.mockReturnValue("access-token");
    apiMocks.get.mockResolvedValue({
      data: {
        id: "user-1",
        email: "donor@example.com",
        role: "donor",
        donor_id: "donor-1",
        hospital_id: null,
        is_active: true,
      },
    });

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("bootstrapping")).toHaveTextContent("no");
    });

    expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");

    act(() => {
      window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
    });

    await waitFor(() => {
      expect(sessionStoreMocks.clear).toHaveBeenCalledTimes(1);
    });

    expect(apiMocks.post).toHaveBeenCalledWith("/auth/logout", {
      refresh_token: "refresh-token",
    });

    expect(screen.getByTestId("authenticated")).toHaveTextContent("no");
    expect(screen.getByTestId("user")).toHaveTextContent("none");
    expect(screen.getByTestId("token")).toHaveTextContent("none");
  });

  it("invalidates session when bootstrap user lookup fails", async () => {
    sessionStoreMocks.getSession.mockReturnValue({
      accessToken: "expired-token",
      expiresAt: "2000-01-01T00:00:00.000Z",
      refreshToken: "refresh-token",
      refreshExpiresAt: "2099-01-02T00:00:00.000Z",
    });
    sessionStoreMocks.getAccessToken.mockReturnValue("expired-token");
    apiMocks.get.mockRejectedValue(new Error("unauthorized"));

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(sessionStoreMocks.clear).toHaveBeenCalledTimes(1);
    });

    expect(screen.getByTestId("authenticated")).toHaveTextContent("no");
    expect(screen.getByTestId("user")).toHaveTextContent("none");
  });
});
