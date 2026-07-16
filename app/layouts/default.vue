<script setup lang="ts">
const route = useRoute();
const pageTitle = computed(() => {
  const path = route.path;
  if (path.startsWith("/members")) return "メンバー";
  if (path.startsWith("/recommendations")) return "推薦プロジェクト";
  if (path.startsWith("/audit")) return "監査ログ";
  if (path.startsWith("/settings")) return "システム設定";
  return "ダッシュボード";
});
useHead(() => ({ title: `${pageTitle.value} | RECO SUPPORT` }));
</script>
<template>
  <div class="app-shell">
    <AppSidebar />
    <div class="main-area">
      <AppTopbar :page-title="pageTitle" />
      <slot />
    </div>
  </div>
</template>
