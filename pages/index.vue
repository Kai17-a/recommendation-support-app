<script setup lang="ts">
definePageMeta({ layout: false })
const router = useRouter()
const email = ref('manager@acme.co.jp')
const password = ref('')
const login = () => router.push('/dashboard')
</script>
<template>
  <main class="simple-login"><form class="simple-login-card" @submit.prevent="login"><h1>ログイン</h1><label>メールアドレス<input v-model="email" type="email" autocomplete="email"></label><label>パスワード<input v-model="password" type="password" autocomplete="current-password"></label><button class="primary full" type="submit">ログイン</button></form></main>
</template>
