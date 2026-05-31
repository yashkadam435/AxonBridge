/**
 * AxonBridge — API Client
 * 
 * Centralized HTTP client with JWT token management,
 * automatic refresh, and error handling.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
  request_id?: string;
}

class AxonBridgeAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('axb_access_token');
  }

  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('axb_refresh_token');
  }

  private setTokens(access: string, refresh: string): void {
    localStorage.setItem('axb_access_token', access);
    localStorage.setItem('axb_refresh_token', refresh);
  }

  private clearTokens(): void {
    localStorage.removeItem('axb_access_token');
    localStorage.removeItem('axb_refresh_token');
  }

  private async refreshAccessToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        this.clearTokens();
        return false;
      }

      const data = await res.json();
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      this.clearTokens();
      return false;
    }
  }

  async request<T>(
    path: string,
    options: RequestInit = {},
  ): Promise<T> {
    const token = this.getAccessToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let res = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    // Auto-refresh on 401
    if (res.status === 401 && token) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        const newToken = this.getAccessToken();
        headers['Authorization'] = `Bearer ${newToken}`;
        res = await fetch(`${this.baseUrl}${path}`, {
          ...options,
          headers,
        });
      } else {
        // Redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/';
        }
        throw new Error('Session expired');
      }
    }

    if (!res.ok) {
      const error: ApiError = await res.json().catch(() => ({
        error_code: 'UNKNOWN',
        message: `HTTP ${res.status}: ${res.statusText}`,
      }));
      throw error;
    }

    return res.json();
  }

  // ---------- Convenience Methods ----------

  get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }

  // ---------- Auth ----------

  async login(email: string, password: string, mfaCode?: string) {
    const data = await this.post<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
    }>('/api/v1/auth/login', { email, password, mfa_code: mfaCode });

    this.setTokens(data.access_token, data.refresh_token);
    return data;
  }

  async logout() {
    try {
      await this.post('/api/v1/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  // ---------- Health ----------

  health() {
    return this.get<{
      status: string;
      version: string;
      uptime_seconds: number;
      checks: Record<string, boolean>;
    }>('/api/v1/health');
  }

  // ---------- Users ----------

  getProfile() {
    return this.get('/api/v1/users/me');
  }

  listUsers(params?: { page?: number; per_page?: number; search?: string }) {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', String(params.page));
    if (params?.per_page) query.set('per_page', String(params.per_page));
    if (params?.search) query.set('search', params.search);
    return this.get(`/api/v1/users?${query}`);
  }

  // ---------- Tenants ----------

  listTenants(params?: { page?: number; per_page?: number }) {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', String(params.page));
    if (params?.per_page) query.set('per_page', String(params.per_page));
    return this.get(`/api/v1/tenants?${query}`);
  }

  // ---------- Roles ----------

  listRoles() {
    return this.get('/api/v1/roles');
  }

  listPermissions() {
    return this.get('/api/v1/roles/permissions');
  }

  // ---------- Audit ----------

  queryAuditLogs(params?: Record<string, string | number>) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) query.set(k, String(v));
      });
    }
    return this.get(`/api/v1/audit/logs?${query}`);
  }

  checkAuditIntegrity() {
    return this.get('/api/v1/audit/integrity-check');
  }
}

// Singleton instance
export const api = new AxonBridgeAPI();
export default AxonBridgeAPI;
