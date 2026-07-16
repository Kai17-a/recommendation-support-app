export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@nuxt/ui"],
  components: [{ path: "~/components", pathPrefix: false }],
  css: [
    "~/assets/css/main.css",
    "~/assets/css/members.css",
    "~/assets/css/nuxt-ui.css",
  ],
  devServer: {
    host: "0.0.0.0",
    port: 3000,
  },
  experimental: {
    appManifest: false,
  },
  compatibilityDate: "2024-11-01",
});
