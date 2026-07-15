<script setup lang="ts">
definePageMeta({ layout: false })
const router = useRouter()
const email = ref('manager@acme.co.jp')
const password = ref('')
const login = () => router.push('/dashboard')
</script>
<template>
  <main class="login-shell">
    <section class="login-brand"><div class="brand-mark">R</div><p class="eyebrow">RECOMMENDATION SUPPORT</p><h1>根拠のある推薦を、<br><em>自信を持って。</em></h1><p class="muted light">メンバーの経験と成長を丁寧に記録し、<br>推薦文作成を支援するためのワークスペース。</p><div class="login-foot">Evidence first · Built for people</div></section>
    <section class="login-form"><div class="form-card"><p class="eyebrow">WELCOME BACK</p><h2>ログイン</h2><p class="muted">あなたのワークスペースにアクセスします。</p><label>メールアドレス<input v-model="email" type="email"></label><label>パスワード<input v-model="password" type="password" placeholder="••••••••"></label><div class="form-row"><label class="check"><input type="checkbox"> ログイン状態を保持</label><a href="#">パスワードを忘れた方</a></div><button class="primary full" @click="login">ログインする <span>→</span></button><p class="demo-note">デモ環境では入力内容を問わずログインできます</p></div></section>
  </main>
</template>
