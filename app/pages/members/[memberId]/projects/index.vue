<script setup lang="ts">
const route = useRoute();
const basePath = computed(() => `/members/${route.params.memberId}/projects`);
</script>
<template>
  <main class="content">
    <AppBackLink
      :to="`/members/${route.params.memberId}`"
      label="メンバー詳細に戻る"
    />
    <AppPageHeader
      eyebrow="PROJECT EXPERIENCE"
      title="案件経験"
      description="案件ごとの成果と報告を管理します。"
      ><template #actions
        ><NuxtLink :to="`${basePath}/new`" class="primary"
          >＋ 案件を追加</NuxtLink
        ></template
      ></AppPageHeader
    >
    <section class="panel">
      <AppPanelHeader
        title="決済プロダクト リニューアル"
        description="2025年4月 — 2026年3月 · Lead Designer"
        ><template #actions
          ><AppStatus tone="green">完了</AppStatus></template
        ></AppPanelHeader
      >
      <p>複雑な決済フローを再設計し、初回利用者の完了率を改善。</p>
      <div class="tags">
        <span>UX設計</span><span>プロダクト戦略</span><span>チームリード</span>
      </div>
      <AppFormActions>
        <NuxtLink :to="`${basePath}/payment-renewal/report`" class="secondary"
          >案件報告を編集</NuxtLink
        ><NuxtLink :to="`${basePath}/payment-renewal/analysis`" class="primary"
          >AI案件分析 →</NuxtLink
        >
      </AppFormActions>
    </section>
  </main>
</template>
