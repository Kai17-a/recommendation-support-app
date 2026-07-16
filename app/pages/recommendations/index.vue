<script setup lang="ts">
const items = [
  ["鈴木 恒一", "Fintech事業部 / プロダクトデザイン責任者", "下書き", "blue"],
  ["山本 美咲", "Platform部 / Engineering Manager", "レビュー中", "orange"],
  ["佐藤 健", "新規事業部 / VP of Product", "確定済み", "green"],
];
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
      <div class="search">⌕ <input placeholder="プロジェクトを検索" /></div>
      <button class="filter">すべてのステータス　⌄</button>
    </div>
    <div class="rec-grid">
      <NuxtLink
        v-for="i in items"
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
  </main>
</template>
