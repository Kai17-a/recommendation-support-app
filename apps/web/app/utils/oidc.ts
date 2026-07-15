import Keycloak from "keycloak-js";

export interface OidcSettings {
  url: string;
  realm: string;
  clientId: string;
}

let client: Keycloak | undefined;

export function getOidcClient(settings: OidcSettings): Keycloak {
  if (!client) {
    client = new Keycloak(settings);
  }
  return client;
}

export async function initializeOidc(settings: OidcSettings): Promise<Keycloak> {
  const keycloak = getOidcClient(settings);
  await keycloak.init({
    onLoad: "check-sso",
    pkceMethod: "S256",
    checkLoginIframe: false,
  });
  return keycloak;
}
