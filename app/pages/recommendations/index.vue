<script setup lang="ts">
const query = ref("");
const status = ref("すべてのステータス");
const statusOptions = [
  "すべてのステータス",
  "下書き",
  "レビュー中",
  "確定済み",
];
const items = [
  ["鈴木 恒一", "Fintech事業部 / プロダクトデザイン責任者", "下書き", "blue"],
  ["山本 美咲", "Platform部 / Engineering Manager", "レビュー中", "orange"],
  ["佐藤 健", "新規事業部 / VP of Product", "確定済み", "green"],
];
const filteredItems = computed(() => {
  const keyword = query.value.trim().toLowerCase();
  return items.filter(
    ([name, description, itemStatus]) =>
      (!keyword || `${name} ${description}`.toLowerCase().includes(keyword)) &&
      (status.value === "すべてのステータス" || status.value === itemStatus),
  );
});
</script>
<template>
  <main class="content">
    <AppPageHeader
      eyebrow="RECOMMENDATIONS"
      title="推薦プロジェクト"
      description="推薦文の作成とレビューを行います。"
    >
      <template #actions
        ><NuxtLink to="/recommendations/new" class="primary"
          >＋ 推薦をはじめる</NuxtLink
        ></template
      >
    </AppPageHeader>
    <div class="toolbar">
      <UInput
        v-model="query"
        icon="i-lucide-search"
        placeholder="プロジェクトを検索"
        aria-label="推薦プロジェクトを検索"
      />
      <USelect
        v-model="status"
        :items="statusOptions"
        aria-label="ステータスで絞り込む"
      />
    </div>
    <div class="rec-grid">
      <NuxtLink
        v-for="i in filteredItems"
        to="/recommendations/1"
        class="panel rec-card"
        ><div class="rec-top">
          <AppAvatar :initial="i[0][0]" tinted />
          <AppStatus :tone="i[3]">{{ i[2] }}</AppStatus>
        </div>
        <h2>{{ i[0] }}</h2>
        <p class="muted">{{ i[1] }}</p>
        <div class="rec-meta">
          <span>最終更新 2時間前</span><span>→</span>
        </div></NuxtLink
      >
    </div>
    <div v-if="filteredItems.length === 0" class="member-empty">
      <strong>条件に一致する推薦プロジェクトはありません</strong>
      <p>検索キーワードまたはステータスの条件を変更してください。</p>
    </div>
  </main>
</template>
