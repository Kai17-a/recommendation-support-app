<script setup lang="ts">
const route = useRoute();
const linked = ref(false);
const recommendationPath = computed(
  () => `/recommendations/${route.params.recommendationId}`,
);
</script>
<template>
  <main class="content narrow">
    <AppBackLink :to="recommendationPath" label="推薦文レビューに戻る" />
    <p class="eyebrow">EVIDENCE DETAIL</p>
    <h1>根拠の詳細</h1>
    <p class="muted">推薦文の各段落に紐づく情報を確認できます。</p>
    <section class="panel evidence-detail">
      <div class="quote-block">
        <span>段落 3</span>
        <p>「チーム全体が前に進める環境をつくってきました。」</p>
      </div>
      <div class="warning">
        <strong>⚠ 根拠が不足している可能性</strong>
        <p>この表現を直接裏付ける記録は見つかりませんでした。</p>
      </div>
      <h3>関連する記録</h3>
      <div class="source">
        <span>◉</span>
        <div>
          <strong>2026年3月 定期評価</strong
          ><small>「周囲を巻き込みながらプロジェクトを推進」</small>
        </div>
      </div>
      <UButton
        :label="linked ? '根拠を紐づけました' : 'この根拠を段落に紐づける'"
        :disabled="linked"
        @click="linked = true"
      />
      <div v-if="linked" class="import-result">
        <strong>根拠を紐づけました</strong>
        <p>段落3の根拠として、人物評価の記録を追加しました。</p>
      </div>
    </section>
  </main>
</template>
