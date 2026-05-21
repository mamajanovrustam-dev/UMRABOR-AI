/** Fetch-based API клиент UMRABOR. Используется во всех frontend-приложениях. */

export type SubjectKind = "umrabor" | "partner" | "client";

export interface ApiClientOptions {
  baseUrl: string;
  /** Хранилище токенов (localStorage в браузере). */
  storageKey?: string;
  /** Колбэк при 401 (например — редирект на /login). */
  onUnauthorized?: () => void;
}

export interface ApiError extends Error {
  status: number;
  detail?: string;
  data?: unknown;
}

interface StoredAuth {
  access_token: string;
  refresh_token: string;
}

export class ApiClient {
  private baseUrl: string;
  private storageKey: string;
  private onUnauthorized?: () => void;

  constructor(opts: ApiClientOptions) {
    this.baseUrl = opts.baseUrl.replace(/\/$/, "");
    this.storageKey = opts.storageKey ?? "umrabor_auth";
    this.onUnauthorized = opts.onUnauthorized;
  }

  // ───────── Auth storage ─────────
  private getAuth(): StoredAuth | null {
    if (typeof window === "undefined") return null;
    try {
      const raw = window.localStorage.getItem(this.storageKey);
      return raw ? (JSON.parse(raw) as StoredAuth) : null;
    } catch {
      return null;
    }
  }

  setAuth(tokens: { access_token: string; refresh_token: string }): void {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(this.storageKey, JSON.stringify(tokens));
  }

  clearAuth(): void {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(this.storageKey);
  }

  get accessToken(): string | null {
    return this.getAuth()?.access_token ?? null;
  }

  // ───────── HTTP ─────────
  async request<T>(
    method: string,
    path: string,
    body?: unknown,
    opts: { auth?: boolean; query?: Record<string, string | number | undefined | null> } = {},
  ): Promise<T> {
    const url = new URL(this.baseUrl + path);
    if (opts.query) {
      for (const [k, v] of Object.entries(opts.query)) {
        if (v !== undefined && v !== null && v !== "") {
          url.searchParams.set(k, String(v));
        }
      }
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const useAuth = opts.auth ?? true;
    if (useAuth) {
      const token = this.accessToken;
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(url.toString(), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401 && useAuth) {
      this.clearAuth();
      this.onUnauthorized?.();
      const err = new Error("Unauthorized") as ApiError;
      err.status = 401;
      throw err;
    }

    let data: unknown = null;
    const text = await res.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
    }

    if (!res.ok) {
      const err = new Error(
        (data as { detail?: string })?.detail ?? `HTTP ${res.status}`,
      ) as ApiError;
      err.status = res.status;
      err.detail = (data as { detail?: string })?.detail;
      err.data = data;
      throw err;
    }

    return data as T;
  }

  get<T>(path: string, query?: Record<string, string | number | undefined | null>): Promise<T> {
    return this.request<T>("GET", path, undefined, { query });
  }
  post<T>(path: string, body?: unknown, query?: Record<string, string | number | undefined | null>): Promise<T> {
    return this.request<T>("POST", path, body, { query });
  }
  put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PUT", path, body);
  }
  delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
  postNoAuth<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("POST", path, body, { auth: false });
  }
  getNoAuth<T>(path: string, query?: Record<string, string | number | undefined | null>): Promise<T> {
    return this.request<T>("GET", path, undefined, { auth: false, query });
  }
}

/** Создаёт API-клиент для текущего приложения. baseUrl берётся из NEXT_PUBLIC_API_URL / VITE_API_URL. */
export function createApiClient(opts: ApiClientOptions): ApiClient {
  return new ApiClient(opts);
}
