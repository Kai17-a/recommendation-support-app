<script setup lang="ts">
const route = useRoute();
const memberPath = computed(() => `/members/${route.params.memberId}`);
const isFormOpen = ref(false);
const completed = ref(false);
const evaluation = ref({ period: "2026年7月 定期評価", comment: "" });
const evaluations = ref([
  {
    period: "2026年3月 定期評価",
    author: "田中 恒一 · 2026/03/31",
    comment:
      "周囲を巻き込みながらプロジェクトを推進し、ユーザー視点でチームの意思決定を支えた。",
  },
]);
const { isPending, run } = useMockAction();
async function saveEvaluation() {
  await run(() => {
    evaluations.value.unshift({
      period: evaluation.value.period,
      author: "田中 恒一 · たった今",
      comment: evaluation.value.comment,
    });
    isFormOpen.value = false;
    completed.value = true;
  });
}
function cancelEvaluation() {
  evaluation.value = { period: "2026年7月 定期評価", comment: "" };
  isFormOpen.value = false;
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink :to="memberPath" label="メンバー詳細に戻る" />
    <AppPageHeader
      eyebrow="PEOPLE EVALUATION"
      title="人物評価"
      description="時系列で評価を記録します。"
      ><template #actions
        ><UButton
          icon="i-lucide-plus"
          label="評価を追加"
          @click="isFormOpen = !isFormOpen" /></template
    ></AppPageHeader>
    <form
      v-if="isFormOpen"
      class="panel form-panel"
      @submit.prevent="saveEvaluation"
    >
      <UFormField label="評価期間" required>
        <UInput v-model="evaluation.period" required />
      </UFormField>
      <UFormField label="評価内容" required>
        <UTextarea
          v-model="evaluation.comment"
          rows="4"
          required
          placeholder="確認できた行動や成果を入力"
        />
      </UFormField>
      <AppFormActions>
        <UButton
          label="キャンセル"
          color="neutral"
          variant="outline"
          @click="cancelEvaluation"
        /><UButton type="submit" label="評価を登録" :loading="isPending" />
      </AppFormActions>
    </form>
    <div v-if="completed" class="import-result">
      <strong>人物評価を登録しました</strong>
      <p>{{ evaluation.period }} の評価を履歴に追加しました。</p>
    </div>
    <section v-for="item in evaluations" :key="item.period" class="panel">
      <AppPanelHeader :title="item.period" :description="item.author"
        ><template #actions
          ><AppStatus tone="green">確定済み</AppStatus></template
        ></AppPanelHeader
      >
      <p>{{ item.comment }}</p>
      <div class="tags"><span>信頼性：高い</span><span>協働性：高い</span></div>
    </section>
  </main>
</template>
