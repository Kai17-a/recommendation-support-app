export interface ApiClientOptions {
  baseUrl: string;
  getToken: () => string | null;
  fetchImpl?: typeof fetch;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: string,
  ) {
    super(message);
  }
}

export function createApiClient(options: ApiClientOptions) {
  const request = async <T>(
    path: string,
    init: RequestInit = {},
  ): Promise<T> => {
    const token = options.getToken();
    if (!token)
      throw new ApiError("ログインが必要です。", 401, "UNAUTHENTICATED");
    const headers = new Headers(init.headers);
    headers.set("Authorization", `Bearer ${token}`);
    headers.set("Accept", "application/json");
    if (init.body && !(init.body instanceof FormData))
      headers.set("Content-Type", "application/json");
    const response = await (options.fetchImpl ?? fetch)(
      `${options.baseUrl}${path}`,
      {
        ...init,
        headers,
      },
    );
    if (!response.ok) {
      const payload = (await response.json().catch(() => ({}))) as {
        error?: { message?: string; code?: string };
      };
      throw new ApiError(
        payload.error?.message ?? `APIエラー (${response.status})`,
        response.status,
        payload.error?.code,
      );
    }
    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  };
  return {
    get: <T>(path: string) => request<T>(path),
    post: <T>(path: string, body?: unknown) =>
      request<T>(path, {
        method: "POST",
        body: body instanceof FormData ? body : JSON.stringify(body),
      }),
    patch: <T>(path: string, body: unknown) =>
      request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  };
}
