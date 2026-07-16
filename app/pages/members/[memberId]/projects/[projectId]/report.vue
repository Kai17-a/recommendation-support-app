<script setup lang="ts">
const route = useRoute();
const projectPath = computed(
  () => `/members/${route.params.memberId}/projects/${route.params.projectId}`,
);
const saved = ref(false);
const reportType = ref("終了報告");
const reportTypeOptions = ["終了報告", "定期報告"];
const report = ref(
  "ユーザーインタビューを通じて課題を整理し、決済フローを再設計しました。チームと協働し、初回利用者の完了率改善につなげました。",
);
const { isPending, run } = useMockAction();
async function saveReport() {
  await run(() => {
    saved.value = true;
  });
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink :to="projectPath" label="案件詳細に戻る" />
    <p class="eyebrow">PROJECT REPORT</p>
    <h1>案件報告を編集</h1>
    <p class="muted">決済プロダクト リニューアル</p>
    <form class="panel form-panel" @submit.prevent="saveReport">
      <UFormField label="報告種別">
        <USelect v-model="reportType" :items="reportTypeOptions" />
      </UFormField>
      <UFormField label="報告内容" required>
        <UTextarea v-model="report" rows="10" required />
      </UFormField>
      <AppFormActions>
        <NuxtLink :to="projectPath" class="secondary">キャンセル</NuxtLink
        ><UButton type="submit" label="保存する" :loading="isPending" />
      </AppFormActions>
    </form>
    <div v-if="saved" class="import-result">
      <strong>案件報告を保存しました</strong>
      <p>変更内容を案件経験に反映しました。</p>
    </div>
  </main>
</template>
