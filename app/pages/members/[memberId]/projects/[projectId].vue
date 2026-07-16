<script setup lang="ts">
const route = useRoute();
const basePath = computed(
  () => `/members/${route.params.memberId}/projects/${route.params.projectId}`,
);
</script>
<template>
  <main class="content narrow">
    <AppBackLink
      :to="`/members/${route.params.memberId}/projects`"
      label="案件経験に戻る"
    />
    <p class="eyebrow">PROJECT DETAIL</p>
    <h1>決済プロダクト リニューアル</h1>
    <p class="muted">2025年4月 — 2026年3月　·　Lead Designer</p>
    <section class="panel project-detail">
      <h2>案件概要</h2>
      <p>
        複雑な決済フローを再設計し、初回利用者の完了率を改善。ユーザーインタビューから課題を構造化し、プロダクトチームと改善を進めました。
      </p>
      <AppFormActions>
        <NuxtLink :to="`${basePath}/report`" class="secondary"
          >案件報告を編集</NuxtLink
        ><NuxtLink :to="`${basePath}/analysis`" class="primary"
          >AI案件分析</NuxtLink
        >
      </AppFormActions>
    </section>
  </main>
</template>
