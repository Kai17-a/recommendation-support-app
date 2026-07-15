import type Keycloak from "keycloak-js";

let client: Keycloak | undefined;

export const tokenStore = {
  bind(value: Keycloak): void {
    client = value;
  },
  get(): string | null {
    return client?.token ?? null;
  },
  clear(): void {
    client = undefined;
  },
};
