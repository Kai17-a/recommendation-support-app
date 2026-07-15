export default defineNuxtConfig({
  compatibilityDate: "2026-07-15",
  devtools: { enabled: true },
  modules: ["@nuxt/eslint"],
  typescript: {
    strict: true,
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? "http://localhost:8000",
      oidcUrl: process.env.NUXT_PUBLIC_OIDC_URL ?? "http://localhost:8080",
      oidcRealm: process.env.NUXT_PUBLIC_OIDC_REALM ?? "recommendation-support",
      oidcClientId:
        process.env.NUXT_PUBLIC_OIDC_CLIENT_ID ?? "recommendation-support-web",
    },
  },
});
