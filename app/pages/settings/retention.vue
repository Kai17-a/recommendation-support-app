<script setup lang="ts">
const saved = ref(false);
const reportRetention = ref("無期限");
const auditRetention = ref("7年間");
const requiresApproval = ref(true);
const reportRetentionOptions = ["無期限", "7年間", "3年間"];
const auditRetentionOptions = ["7年間", "3年間"];
const { isPending, run } = useMockAction();
async function saveSettings() {
  await run(() => {
    saved.value = true;
  });
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink to="/settings" label="システム設定に戻る" />
    <p class="eyebrow">DATA RETENTION</p>
    <h1>データ保持設定</h1>
    <p class="muted">論理削除と監査ログの保持期間を管理します。</p>
    <form class="panel form-panel" @submit.prevent="saveSettings">
      <UFormField label="案件報告の保持期間">
        <USelect v-model="reportRetention" :items="reportRetentionOptions" />
      </UFormField>
      <UFormField label="監査ログの保持期間">
        <USelect v-model="auditRetention" :items="auditRetentionOptions" />
      </UFormField>
      <UCheckbox
        v-model="requiresApproval"
        label="物理削除前に管理者承認を必須にする"
      />
      <AppFormActions>
        <UButton type="submit" label="設定を保存" :loading="isPending" />
      </AppFormActions>
      <div v-if="saved" class="save-message">
        データ保持設定を保存しました。
      </div>
    </form>
  </main>
</template>
