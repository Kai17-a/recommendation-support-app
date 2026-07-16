<script setup lang="ts">
const route = useRoute();
const completed = ref(false);
const project = ref({ name: "", period: "", role: "", description: "" });
const createdProjectName = ref("");
const { isPending, run } = useMockAction();
const projectsPath = computed(
  () => `/members/${route.params.memberId}/projects`,
);
async function saveProject() {
  await run(() => {
    createdProjectName.value = project.value.name;
    completed.value = true;
  });
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink :to="projectsPath" label="案件経験に戻る" />
    <p class="eyebrow">NEW PROJECT</p>
    <h1>案件経験を追加</h1>
    <form class="panel form-panel" @submit.prevent="saveProject">
      <UFormField label="案件名" required>
        <UInput
          v-model="project.name"
          required
          placeholder="例: 新規決済機能の設計"
        />
      </UFormField>
      <UFormField label="期間" required>
        <UInput
          v-model="project.period"
          required
          placeholder="例: 2026年4月 — 2026年9月"
        />
      </UFormField>
      <UFormField label="役割" required>
        <UInput v-model="project.role" required placeholder="担当した役割" />
      </UFormField>
      <UFormField label="概要" required>
        <UTextarea
          v-model="project.description"
          rows="5"
          required
          placeholder="案件の概要と成果"
        />
      </UFormField>
      <AppFormActions>
        <NuxtLink :to="projectsPath" class="secondary">キャンセル</NuxtLink
        ><UButton type="submit" label="案件経験を登録" :loading="isPending" />
      </AppFormActions>
    </form>
    <div v-if="completed" class="import-result">
      <strong>案件経験を登録しました</strong>
      <p>{{ createdProjectName }} を案件経験に追加しました。</p>
      <NuxtLink :to="projectsPath">案件経験一覧へ戻る →</NuxtLink>
    </div>
  </main>
</template>
