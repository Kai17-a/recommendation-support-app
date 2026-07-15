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
    },
  },
});
