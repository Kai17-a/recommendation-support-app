import { describe, expect, it, vi } from "vitest";

import { ApiError, createApiClient } from "../app/utils/api-client";

describe("API client", () => {
  it("Bearer tokenを付けてJSONを取得する", async () => {
    const fetchImpl = vi.fn(async (_input, init) => {
      expect(new Headers(init?.headers).get("Authorization")).toBe(
        "Bearer test-token",
      );
      return new Response(JSON.stringify([{ id: "1" }]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }) as typeof fetch;
    const api = createApiClient({
      baseUrl: "https://api.example",
      getToken: () => "test-token",
      fetchImpl,
    });
    await expect(api.get("/api/v1/members")).resolves.toEqual([{ id: "1" }]);
  });

  it("tokenがない場合は通信しない", async () => {
    const fetchImpl = vi.fn() as unknown as typeof fetch;
    const api = createApiClient({
      baseUrl: "https://api.example",
      getToken: () => null,
      fetchImpl,
    });
    await expect(api.get("/api/v1/members")).rejects.toMatchObject({
      status: 401,
    });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("APIの安全なエラー本文を利用者へ返す", async () => {
    const fetchImpl = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            error: { code: "FORBIDDEN", message: "参照できません。" },
          }),
          {
            status: 403,
          },
        ),
    ) as typeof fetch;
    const api = createApiClient({
      baseUrl: "https://api.example",
      getToken: () => "token",
      fetchImpl,
    });
    await expect(api.get("/private")).rejects.toEqual(
      new ApiError("参照できません。", 403, "FORBIDDEN"),
    );
  });
});
