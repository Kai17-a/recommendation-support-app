<script setup lang="ts">
const created = ref(false);
const createdId = ref("");
const { isPending, run } = useMockAction();
const memberOptions = [
  "鈴木 恒一 — Senior Product Designer",
  "山本 美咲 — Frontend Engineer",
];
const recommendation = ref({
  member: "鈴木 恒一 — Senior Product Designer",
  purpose: "",
  target: "",
  emphasis: "",
});
async function createRecommendation() {
  await run(() => {
    createdId.value = `rec-${Date.now()}`;
    created.value = true;
  });
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink to="/recommendations" label="推薦プロジェクトに戻る" />
    <p class="eyebrow">NEW RECOMMENDATION</p>
    <h1>推薦プロジェクトをはじめる</h1>
    <p class="muted">推薦したいメンバーと、推薦の目的を教えてください。</p>
    <form class="panel form-panel" @submit.prevent="createRecommendation">
      <UFormField label="推薦対象">
        <USelect v-model="recommendation.member" :items="memberOptions" />
      </UFormField>
      <UFormField label="推薦の目的" required>
        <UInput
          v-model="recommendation.purpose"
          required
          placeholder="例: Fintechプロダクト責任者への推薦"
        />
      </UFormField>
      <UFormField label="推薦先" required>
        <UInput
          v-model="recommendation.target"
          required
          placeholder="推薦先の役職・企業など"
        />
      </UFormField>
      <UFormField label="強調したいポイント">
        <UTextarea
          v-model="recommendation.emphasis"
          rows="4"
          placeholder="この推薦で特に伝えたいこと"
        />
      </UFormField>
      <AppFormActions>
        <NuxtLink to="/recommendations" class="secondary">キャンセル</NuxtLink
        ><UButton
          type="submit"
          label="推薦プロジェクトを作成"
          :loading="isPending"
        />
      </AppFormActions>
    </form>
    <div v-if="created" class="import-result">
      <strong>推薦プロジェクトを作成しました</strong>
      <p>{{ recommendation.member }} の推薦文作成を開始できます。</p>
      <NuxtLink :to="`/recommendations/${createdId}`"
        >推薦文の編集へ →</NuxtLink
      >
    </div>
  </main>
</template>
