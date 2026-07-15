const TOKEN_KEY = "recommendation-support.oidc-access-token";

export const tokenStore = {
  get(): string | null {
    return import.meta.client ? sessionStorage.getItem(TOKEN_KEY) : null;
  },
  set(token: string): void {
    if (import.meta.client) sessionStorage.setItem(TOKEN_KEY, token);
  },
  clear(): void {
    if (import.meta.client) sessionStorage.removeItem(TOKEN_KEY);
  },
};
