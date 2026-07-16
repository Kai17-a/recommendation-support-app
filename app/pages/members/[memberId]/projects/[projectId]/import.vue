<script setup lang="ts">
const route = useRoute();
const imported = ref(false);
const selectedFile = ref<File | null>(null);
const keepSource = ref(true);
const { isPending, run } = useMockAction();
const projectPath = computed(
  () => `/members/${route.params.memberId}/projects/${route.params.projectId}`,
);
async function importMarkdown() {
  if (!selectedFile.value) return;
  await run(() => {
    imported.value = true;
  }, 700);
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink :to="projectPath" label="案件詳細に戻る" />
    <p class="eyebrow">MARKDOWN IMPORT</p>
    <h1>Markdown取り込み</h1>
    <p class="muted">報告ファイルから案件情報とスキル候補を抽出します。</p>
    <section class="panel form-panel">
      <UFormField label="対象メンバー">
        <UInput value="鈴木 恒一" disabled />
      </UFormField>
      <UFormField label="対象案件">
        <UInput value="決済プロダクト リニューアル" disabled />
      </UFormField>
      <UFormField label="Markdownファイル" required>
        <UFileUpload
          v-model="selectedFile"
          accept=".md,text/markdown"
          label="Markdownファイルを選択"
          description=".md ファイルをここにドロップ"
        />
      </UFormField>
      <UCheckbox v-model="keepSource" label="元ファイルを保存する" />
      <AppFormActions>
        <NuxtLink :to="projectPath" class="secondary">キャンセル</NuxtLink
        ><UButton
          label="解析を実行する"
          :disabled="!selectedFile"
          :loading="isPending"
          @click="importMarkdown"
        />
      </AppFormActions>
      <div v-if="imported" class="import-result">
        <strong>解析が完了しました</strong>
        <p>案件報告 1件、スキル候補 3件、警告 1件を検出しました。</p>
        <NuxtLink :to="`${projectPath}/report`">結果を確認する →</NuxtLink>
      </div>
    </section>
  </main>
</template>
