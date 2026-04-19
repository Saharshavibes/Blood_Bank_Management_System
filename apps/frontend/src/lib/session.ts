export interface AuthSession {
  accessToken: string;
  expiresAt: string;
  refreshToken: string;
  refreshExpiresAt: string;
}

const SESSION_KEY = "bbms_session";

let inMemorySession: AuthSession | null = null;

function canUseSessionStorage(): boolean {
  return typeof window !== "undefined" && typeof window.sessionStorage !== "undefined";
}

function parseTimestamp(value: string): number | null {
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) {
    return null;
  }
  return timestamp;
}

function hasExpired(expiresAt: string): boolean {
  const expiresAtTimestamp = parseTimestamp(expiresAt);
  if (expiresAtTimestamp === null) {
    return true;
  }
  return Date.now() >= expiresAtTimestamp;
}

function parsePersistedSession(rawValue: string | null): AuthSession | null {
  if (!rawValue) {
    return null;
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<AuthSession>;
    if (
      typeof parsed.accessToken !== "string"
      || typeof parsed.expiresAt !== "string"
      || typeof parsed.refreshToken !== "string"
      || typeof parsed.refreshExpiresAt !== "string"
    ) {
      return null;
    }

    if (parseTimestamp(parsed.expiresAt) === null || parseTimestamp(parsed.refreshExpiresAt) === null) {
      return null;
    }

    return {
      accessToken: parsed.accessToken,
      expiresAt: parsed.expiresAt,
      refreshToken: parsed.refreshToken,
      refreshExpiresAt: parsed.refreshExpiresAt,
    };
  } catch {
    return null;
  }
}

export const sessionStore = {
  getSession(): AuthSession | null {
    if (inMemorySession) {
      if (hasExpired(inMemorySession.refreshExpiresAt)) {
        this.clear();
        return null;
      }
      return inMemorySession;
    }

    if (!canUseSessionStorage()) {
      return null;
    }

    const persistedSession = parsePersistedSession(window.sessionStorage.getItem(SESSION_KEY));
    if (!persistedSession || hasExpired(persistedSession.refreshExpiresAt)) {
      this.clear();
      return null;
    }

    inMemorySession = persistedSession;
    return persistedSession;
  },

  getAccessToken(): string | null {
    const session = this.getSession();
    if (!session || hasExpired(session.expiresAt)) {
      return null;
    }
    return session.accessToken;
  },

  getRefreshToken(): string | null {
    const session = this.getSession();
    if (!session || hasExpired(session.refreshExpiresAt)) {
      return null;
    }
    return session.refreshToken;
  },

  setSession(session: AuthSession): void {
    inMemorySession = session;
    if (canUseSessionStorage()) {
      window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
    }
  },

  clear(): void {
    inMemorySession = null;
    if (canUseSessionStorage()) {
      window.sessionStorage.removeItem(SESSION_KEY);
    }
  },
};
