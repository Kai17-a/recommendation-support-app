<script setup lang="ts">
definePageMeta({ layout: false });
const router = useRouter();
const email = ref("manager@acme.co.jp");
const password = ref("");
const { isPending, run } = useMockAction();
async function login() {
  await run(() => router.push("/dashboard"));
}
</script>
<template>
  <main class="simple-login">
    <form class="simple-login-card" @submit.prevent="login">
      <h1>ログイン</h1>
      <label
        >メールアドレス<input
          v-model="email"
          type="email"
          autocomplete="email"
          required /></label
      ><label
        >パスワード<input
          v-model="password"
          type="password"
          autocomplete="current-password"
          required /></label
      ><button class="primary full" type="submit" :disabled="isPending">
        {{ isPending ? "ログイン中..." : "ログイン" }}
      </button>
    </form>
  </main>
</template>
