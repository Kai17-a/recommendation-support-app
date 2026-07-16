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
      <UFormField label="メールアドレス" required>
        <UInput v-model="email" type="email" autocomplete="email" required />
      </UFormField>
      <UFormField label="パスワード" required>
        <UInput
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </UFormField>
      <UButton type="submit" block :loading="isPending" label="ログイン" />
    </form>
  </main>
</template>
