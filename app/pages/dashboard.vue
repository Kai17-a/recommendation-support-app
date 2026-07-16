<script setup lang="ts">
const stats = [
  ["進行中の推薦", "6", "今月 +2"],
  ["登録メンバー", "24", "前月比 +3"],
  ["未対応の警告", "4", "確認が必要"],
  ["今月の確定", "3", "先月 +1"],
];
const projects = [
  ["鈴木 恒一", "Senior Product Designer", "Fintech事業部", "下書き", "blue"],
  ["山本 美咲", "Frontend Engineer", "Platform部", "レビュー中", "orange"],
  ["佐藤 健", "Product Manager", "新規事業部", "確定済み", "green"],
];
</script>

<template>
  <main class="content">
    <AppPageHeader
      eyebrow="THURSDAY, JULY 16, 2026"
      title="ダッシュボード"
      description="推薦プロジェクトと確認が必要な項目を確認します。"
    >
      <template #actions
        ><NuxtLink to="/recommendations/new" class="primary"
          >＋ 推薦をはじめる</NuxtLink
        ></template
      >
    </AppPageHeader>
    <div class="stats">
      <div v-for="stat in stats" :key="stat[0]" class="stat-card">
        <span>{{ stat[0] }}</span
        ><strong>{{ stat[1] }}</strong
        ><small :class="stat[2].includes('確認') ? 'warn' : ''">{{
          stat[2]
        }}</small>
      </div>
    </div>
    <div class="dashboard-grid">
      <section class="panel">
        <AppPanelHeader
          title="最近の推薦プロジェクト"
          description="あなたが担当しているプロジェクト"
          ><template #actions
            ><NuxtLink to="/recommendations">すべて見る →</NuxtLink></template
          ></AppPanelHeader
        >
        <div v-for="project in projects" :key="project[0]" class="project-row">
          <AppAvatar :initial="project[0][0]" tinted />
          <div class="project-main">
            <strong>{{ project[0] }}</strong
            ><span>{{ project[1] }} · {{ project[2] }}</span>
          </div>
          <AppStatus :tone="project[4]">{{ project[3] }}</AppStatus>
          ><NuxtLink to="/recommendations/1" class="arrow">→</NuxtLink>
        </div>
      </section>
      <section class="panel activity">
        <AppPanelHeader
          title="確認が必要なこと"
          description="見落としのないように確認しましょう"
        />
        <div class="notice">
          <span class="notice-icon">!</span>
          <div>
            <strong>4件のAI警告があります</strong>
            <p>根拠が不足している項目を確認してください</p>
            <NuxtLink to="/recommendations/1">警告を確認する →</NuxtLink>
          </div>
        </div>
        <div class="notice soft">
          <span class="notice-icon blue-bg">↗</span>
          <div>
            <strong>鈴木さんの案件報告が更新されました</strong>
            <p>2時間前 · 田中 恒一</p>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>
