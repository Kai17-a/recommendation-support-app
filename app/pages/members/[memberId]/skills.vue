<script setup lang="ts">
const route = useRoute();
const memberPath = computed(() => `/members/${route.params.memberId}`);
const isFormOpen = ref(false);
const completed = ref(false);
const completedSkill = ref("");
const skill = ref("");
const skills = ref([
  ["ユーザー中心設計", "案件報告から確認"],
  ["ステークホルダー調整", "人物評価から確認"],
  ["チームマネジメント", "候補・要確認"],
]);
const { isPending, run } = useMockAction();
async function saveSkill() {
  const name = skill.value.trim();
  if (!name) return;
  await run(() => {
    skills.value.unshift([name, "手動で登録"]);
    completedSkill.value = name;
    skill.value = "";
    isFormOpen.value = false;
    completed.value = true;
  });
}
function cancelSkill() {
  skill.value = "";
  isFormOpen.value = false;
}
</script>
<template>
  <main class="content narrow">
    <AppBackLink :to="memberPath" label="メンバー詳細に戻る" />
    <AppPageHeader
      eyebrow="SKILLS"
      title="スキル管理"
      description="案件報告から抽出されたスキル候補を確認します。"
      ><template #actions
        ><UButton
          icon="i-lucide-plus"
          label="スキルを追加"
          @click="isFormOpen = !isFormOpen" /></template
    ></AppPageHeader>
    <form
      v-if="isFormOpen"
      class="panel form-panel"
      @submit.prevent="saveSkill"
    >
      <UFormField label="スキル名" required>
        <UInput v-model="skill" required placeholder="例: ユーザーリサーチ" />
      </UFormField>
      <UFormField label="登録理由">
        <UTextarea rows="3" placeholder="根拠となる案件経験や評価を入力" />
      </UFormField>
      <AppFormActions>
        <UButton
          label="キャンセル"
          color="neutral"
          variant="outline"
          @click="cancelSkill"
        /><UButton type="submit" label="スキルを登録" :loading="isPending" />
      </AppFormActions>
    </form>
    <div v-if="completed" class="import-result">
      <strong>スキルを登録しました</strong>
      <p>{{ completedSkill }} をメンバーのスキルとして追加しました。</p>
    </div>
    <section class="panel skill-list">
      <div v-for="item in skills" :key="item[0]" class="skill">
        <span>{{ item[0] }}</span
        ><b>{{ item[1] }}</b>
      </div>
    </section>
  </main>
</template>
