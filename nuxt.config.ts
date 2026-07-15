export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },
  experimental: {
    appManifest: false
  },
  compatibilityDate: '2024-11-01'
})
