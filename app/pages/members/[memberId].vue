<script setup lang="ts">
const route = useRoute();
const memberId = computed(() => String(route.params.memberId));
const profiles: Record<
  string,
  {
    name: string;
    role: string;
    department: string;
    initial: string;
    projectCount: number;
  }
> = {
  suzuki: {
    name: "鈴木 恒一",
    role: "Senior Product Designer",
    department: "Fintech事業部",
    initial: "鈴",
    projectCount: 4,
  },
  yamamoto: {
    name: "山本 美咲",
    role: "Frontend Engineer",
    department: "Platform部",
    initial: "山",
    projectCount: 6,
  },
  sato: {
    name: "佐藤 健",
    role: "Product Manager",
    department: "新規事業部",
    initial: "佐",
    projectCount: 3,
  },
  takahashi: {
    name: "高橋 里奈",
    role: "UX Researcher",
    department: "Fintech事業部",
    initial: "高",
    projectCount: 2,
  },
  ito: {
    name: "伊藤 智也",
    role: "Backend Engineer",
    department: "Platform部",
    initial: "伊",
    projectCount: 5,
  },
  watanabe: {
    name: "渡辺 彩",
    role: "Business Designer",
    department: "新規事業部",
    initial: "渡",
    projectCount: 2,
  },
};
const member = computed(() => profiles[memberId.value] ?? profiles.suzuki);
const basePath = computed(() => `/members/${memberId.value}`);
const tabs = computed(() => [
  { label: "概要", to: basePath.value },
  { label: "案件経験", to: `${basePath.value}/projects` },
  { label: "人物評価", to: `${basePath.value}/evaluation` },
  { label: "スキル", to: `${basePath.value}/skills` },
]);
const isEditOpen = ref(false);
const saved = ref(false);
const profileDetails = ref({
  role: member.value.role,
  department: member.value.department,
});
const editableProfile = ref({ ...profileDetails.value });
const { isPending, run } = useMockAction();
async function saveProfile() {
  await run(() => {
    profileDetails.value = { ...editableProfile.value };
    saved.value = true;
    isEditOpen.value = false;
  });
}
</script>

<template>
  <main class="content">
    <AppBackLink to="/members" label="メンバー一覧に戻る" />
    <div class="profile-head">
      <AppAvatar :initial="member.initial" size="large" />
      <div>
        <p class="eyebrow">MEMBER PROFILE</p>
        <h1>{{ member.name }}</h1>
        <p class="muted">
          {{ profileDetails.role }}　·　{{ profileDetails.department }}
        </p>
      </div>
      <div class="profile-actions">
        <UButton
          label="編集"
          color="neutral"
          variant="outline"
          @click="
            editableProfile = { ...profileDetails };
            isEditOpen = true;
          "
        /><NuxtLink to="/recommendations/new" class="primary"
          >✦ このメンバーを推薦</NuxtLink
        >
      </div>
    </div>
    <form
      v-if="isEditOpen"
      class="panel form-panel"
      @submit.prevent="saveProfile"
    >
      <label>役割<input v-model="editableProfile.role" required /></label>
      <label>部署<input v-model="editableProfile.department" required /></label>
      <AppFormActions>
        <UButton
          label="キャンセル"
          color="neutral"
          variant="outline"
          @click="
            editableProfile = { ...profileDetails };
            isEditOpen = false;
          "
        />
        <UButton type="submit" label="変更を保存" :loading="isPending" />
      </AppFormActions>
    </form>
    <div v-if="saved" class="import-result">
      <strong>メンバー情報を保存しました</strong>
      <p>表示内容に変更を反映しました。</p>
    </div>
    <nav class="tabs" aria-label="メンバー詳細タブ">
      <NuxtLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        :class="{ selected: route.path === tab.to }"
        >{{ tab.label }}</NuxtLink
      >
    </nav>
    <div class="detail-grid">
      <section class="panel">
        <AppPanelHeader
          title="最近の案件経験"
          :description="`${member.name}さんが関わったプロジェクト`"
        >
          <template #actions
            ><NuxtLink :to="`${basePath}/projects/new`" class="text-btn"
              >＋ 案件を追加</NuxtLink
            ></template
          >
        </AppPanelHeader>
        <div class="timeline">
          <div class="timeline-item">
            <span class="dot"></span>
            <div>
              <div class="line-title">
                <strong>決済プロダクト リニューアル</strong
                ><AppStatus tone="green">完了</AppStatus>
              </div>
              <p class="muted">2025年4月 — 2026年3月　·　Lead Designer</p>
              <p>複雑な決済フローを再設計し、初回利用者の完了率を改善。</p>
              <div class="tags">
                <span>UX設計</span><span>プロダクト戦略</span
                ><span>チームリード</span>
              </div>
              <div class="inline-links">
                <NuxtLink :to="`${basePath}/projects/payment-renewal`"
                  >案件詳細 →</NuxtLink
                ><NuxtLink :to="`${basePath}/projects/payment-renewal/report`"
                  >報告を編集</NuxtLink
                ><NuxtLink :to="`${basePath}/projects/payment-renewal/import`"
                  >Markdown取り込み</NuxtLink
                >
              </div>
            </div>
          </div>
          <div class="timeline-item">
            <span class="dot gray"></span>
            <div>
              <div class="line-title">
                <strong>加盟店管理ダッシュボード</strong
                ><AppStatus>進行中</AppStatus>
              </div>
              <p class="muted">2024年10月 — 2025年3月　·　Designer</p>
              <p>
                ユーザーインタビューから業務フローを整理し、運用コストを削減。
              </p>
            </div>
          </div>
        </div>
      </section>
      <aside class="panel side-summary">
        <h2>スキル・特徴</h2>
        <div class="skill"><span>ユーザー中心設計</span><b>Experience</b></div>
        <div class="skill">
          <span>ステークホルダー調整</span><b>Experience</b>
        </div>
        <div class="skill"><span>チームマネジメント</span><b>Candidate</b></div>
        <hr />
        <h2>人物評価</h2>
        <p class="muted">最終評価　2026年3月</p>
        <div class="rating">高い信頼性 <span>●●●●○</span></div>
        <NuxtLink :to="`${basePath}/evaluation`" class="text-btn"
          >評価履歴を見る →</NuxtLink
        >
      </aside>
    </div>
  </main>
</template>
