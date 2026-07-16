<script setup lang="ts">
const route = useRoute();
const nav = [
  { label: "ダッシュボード", icon: "⌂", to: "/dashboard" },
  { label: "メンバー", icon: "♙", to: "/members" },
  { label: "推薦プロジェクト", icon: "✦", to: "/recommendations" },
  { label: "監査ログ", icon: "≡", to: "/audit" },
];
</script>

<template>
  <aside class="sidebar">
    <div class="side-logo">
      <span>R</span>
      <div>RECO<span>SUPPORT</span></div>
    </div>
    <p class="side-label">WORKSPACE</p>
    <nav>
      <NuxtLink
        v-for="item in nav"
        :key="item.to"
        :to="item.to"
        :class="{ active: route.path.startsWith(item.to) }"
      >
        <b>{{ item.icon }}</b
        >{{ item.label }}
      </NuxtLink>
    </nav>
    <div class="side-user">
      <AppAvatar initial="田" size="small" />
      <div><strong>田中 恒一</strong><small>部長・マネージャー</small></div>
      <NuxtLink
        to="/settings"
        class="account-settings-link"
        aria-label="システム設定へ移動"
        title="システム設定"
      >
        ⚙
      </NuxtLink>
    </div>
  </aside>
</template>
