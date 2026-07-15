import Keycloak from "keycloak-js";

export interface OidcSettings {
  url: string;
  realm: string;
  clientId: string;
}

let client: Keycloak | undefined;
let initialization: Promise<boolean> | undefined;

export function getOidcClient(settings: OidcSettings): Keycloak {
  if (!client) {
    client = new Keycloak(settings);
  }
  return client;
}

export async function initializeOidc(settings: OidcSettings): Promise<Keycloak> {
  const keycloak = getOidcClient(settings);
  initialization ??= keycloak.init({
    onLoad: "check-sso",
    pkceMethod: "S256",
    checkLoginIframe: false,
  });
  try {
    await initialization;
  } catch (error) {
    initialization = undefined;
    throw error;
  }
  return keycloak;
}
