<script setup lang="ts">
definePageMeta({ alias: ["/settings/llm"] });

const saved = ref(false);
const connectionState = ref<"idle" | "testing" | "success">("idle");
const apiKey = ref("mock-api-key");
const { isPending, run } = useMockAction();
const config = ref({
  baseUrl: "https://ai-gateway.internal/v1",
  model: "claude-3-7-sonnet",
});
async function testConnection() {
  connectionState.value = "testing";
  await run(() => {
    connectionState.value = "success";
  }, 600);
}
async function saveSettings() {
  await run(() => {
    saved.value = true;
  });
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink to="/settings" label="設定に戻る" />
    <p class="eyebrow">LLM CONFIGURATION</p>
    <h1>LLM設定</h1>
    <p class="muted">推薦文生成や案件分析で利用する言語モデルを設定します。</p>
    <form class="panel form-panel llm-form" @submit.prevent="saveSettings">
      <h2>接続設定</h2>
      <p class="muted section-note">
        AI Gateway 経由で接続します。APIキーは画面上に表示されません。
      </p>
      <label>Base URL<input v-model="config.baseUrl" required /></label
      ><label>APIキー<input v-model="apiKey" type="password" required /></label>
      <label
        >既定モデル<input
          v-model="config.model"
          required
          placeholder="例: claude-3-7-sonnet"
      /></label>
      <AppFormActions>
        <UButton
          type="button"
          color="neutral"
          variant="outline"
          :loading="connectionState === 'testing'"
          label="接続テスト"
          @click="testConnection"
        /><UButton type="submit" label="設定を保存" :loading="isPending" />
      </AppFormActions>
      <div v-if="connectionState === 'success'" class="import-result">
        <strong>接続に成功しました</strong>
        <p>{{ config.baseUrl }} へ接続できました。</p>
      </div>
      <div v-if="saved" class="save-message">設定を保存しました。</div>
    </form>
  </main>
</template>
