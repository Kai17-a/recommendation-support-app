<script setup lang="ts">
const router = useRouter();
const route = useRoute();
const evidencePath = computed(
  () => `/recommendations/${route.params.recommendationId}/evidence`,
);
const text = ref(
  "鈴木さんは、複雑な課題を構造化し、チームと共に解決へ導くプロダクトデザイナーです。\n\n決済プロダクトのリニューアルでは、ユーザーインタビューを起点に課題を整理し、設計からリリースまでをリードしました。その結果、初回利用者の完了率を改善しています。\n\nまた、異なる専門性を持つメンバーとの対話を大切にし、チーム全体が前に進める環境をつくってきました。",
);
const saved = ref(false);
const regenerated = ref(false);
const { isPending, run } = useMockAction();
async function saveDraft() {
  await run(() => {
    saved.value = true;
  });
}
async function regenerateDraft() {
  await run(() => {
    text.value = `${text.value}\n\n関係者と丁寧に合意を形成し、継続的な改善を推進した実績も確認できます。`;
    regenerated.value = true;
    saved.value = false;
  }, 700);
}
</script>
<template>
  <main class="content">
    <AppBackLink to="/recommendations" label="推薦プロジェクトに戻る" />
    <AppPageHeader
      eyebrow="DRAFT · LAST SAVED 2 HOURS AGO"
      title="鈴木 恒一さんの推薦文"
      description="Fintechプロダクト責任者への推薦"
    >
      <template #actions>
        <button class="secondary" :disabled="isPending" @click="saveDraft">
          {{ saved ? "保存済み" : "下書き保存" }}
        </button>
        <button class="primary" @click="router.push(evidencePath)">
          最終確定 →
        </button>
      </template>
    </AppPageHeader>
    <div class="review-grid">
      <section class="panel editor">
        <div class="editor-bar">
          <strong>推薦文　<span>v2</span></strong
          ><button
            class="secondary"
            :disabled="isPending"
            @click="regenerateDraft"
          >
            {{ isPending ? "再生成中..." : "✦ AIで再生成" }}
          </button>
        </div>
        <UTextarea v-model="text" class="editor-textarea" autoresize />
        <div class="editor-foot">
          <span class="muted">AI生成部分を含みます　·　1,284文字</span
          ><AppStatus tone="orange">⚠ 1件の警告</AppStatus>
        </div>
        <div v-if="saved || regenerated" class="editor-message">
          {{
            regenerated
              ? "推薦文を再生成しました。内容を確認して保存してください。"
              : "下書きを保存しました。"
          }}
        </div>
      </section>
      <aside class="panel evidence">
        <h2>根拠と確認事項</h2>
        <div class="warning">
          <strong>根拠が不足している可能性</strong>
          <p>「チーム全体が前に進める環境」の根拠を確認してください。</p>
          <NuxtLink :to="evidencePath">根拠の詳細を見る →</NuxtLink>
        </div>
        <h3>参照した情報</h3>
        <div class="source">
          <span>▣</span>
          <div>
            <strong>決済プロダクト リニューアル</strong
            ><small>案件報告 · 2026/03/28</small>
          </div>
        </div>
        <div class="source">
          <span>◉</span>
          <div>
            <strong>2026年3月 定期評価</strong
            ><small>人物評価 · 2026/03/31</small>
          </div>
        </div>
        <hr />
        <p class="muted small">
          生成モデル　claude-3-7-sonnet<br />生成日時　2026/07/16 09:42
        </p>
      </aside>
    </div>
  </main>
</template>
