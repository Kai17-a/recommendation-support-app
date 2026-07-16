<script setup lang="ts">
const saved = ref(false);
const reportRetention = ref("無期限");
const auditRetention = ref("7年間");
const requiresApproval = ref(true);
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
      <label
        >案件報告の保持期間<select v-model="reportRetention">
          <option>無期限</option>
          <option>7年間</option>
          <option>3年間</option>
        </select></label
      ><label
        >監査ログの保持期間<select v-model="auditRetention">
          <option>7年間</option>
          <option>3年間</option>
        </select></label
      ><label class="check"
        ><input v-model="requiresApproval" type="checkbox" />
        物理削除前に管理者承認を必須にする</label
      >
      <AppFormActions>
        <UButton type="submit" label="設定を保存" :loading="isPending" />
      </AppFormActions>
      <div v-if="saved" class="save-message">
        データ保持設定を保存しました。
      </div>
    </form>
  </main>
</template>
