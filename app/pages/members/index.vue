<script setup lang="ts">
type Member = {
  name: string;
  role: string;
  department: string;
  projects: number;
  updatedAt: string;
  id: string;
  tone: string;
};
const members = ref<Member[]>([
  {
    name: "鈴木 恒一",
    role: "Senior Product Designer",
    department: "Fintech事業部",
    projects: 4,
    updatedAt: "2026/07/15",
    id: "suzuki",
    tone: "teal",
  },
  {
    name: "山本 美咲",
    role: "Frontend Engineer",
    department: "Platform部",
    projects: 6,
    updatedAt: "2026/07/14",
    id: "yamamoto",
    tone: "gold",
  },
  {
    name: "佐藤 健",
    role: "Product Manager",
    department: "新規事業部",
    projects: 3,
    updatedAt: "2026/07/12",
    id: "sato",
    tone: "coral",
  },
  {
    name: "高橋 里奈",
    role: "UX Researcher",
    department: "Fintech事業部",
    projects: 2,
    updatedAt: "2026/07/10",
    id: "takahashi",
    tone: "blue",
  },
  {
    name: "伊藤 智也",
    role: "Backend Engineer",
    department: "Platform部",
    projects: 5,
    updatedAt: "2026/07/08",
    id: "ito",
    tone: "green",
  },
  {
    name: "渡辺 彩",
    role: "Business Designer",
    department: "新規事業部",
    projects: 2,
    updatedAt: "2026/07/04",
    id: "watanabe",
    tone: "rose",
  },
]);
const query = ref("");
const department = ref("すべての部署");
const isAddDialogOpen = ref(false);
const completedMember = ref("");
const newMember = ref({ name: "", role: "", department: "Fintech事業部" });
const { isPending, run } = useMockAction();
const departments = [
  "すべての部署",
  "Fintech事業部",
  "Platform部",
  "新規事業部",
];
const filteredMembers = computed(() => {
  const keyword = query.value.trim().toLowerCase();
  return members.value.filter((member) => {
    const matchesQuery =
      !keyword ||
      [member.name, member.role, member.department]
        .join(" ")
        .toLowerCase()
        .includes(keyword);
    return (
      matchesQuery &&
      (department.value === "すべての部署" ||
        member.department === department.value)
    );
  });
});
async function addMember() {
  if (!newMember.value.name.trim() || !newMember.value.role.trim()) return;
  await run(() => {
    members.value.unshift({
      name: newMember.value.name.trim(),
      role: newMember.value.role.trim(),
      department: newMember.value.department,
      projects: 0,
      updatedAt: "たった今",
      id: `member-${members.value.length + 1}`,
      tone: "teal",
    });
    completedMember.value = newMember.value.name.trim();
    newMember.value = { name: "", role: "", department: "Fintech事業部" };
    isAddDialogOpen.value = false;
  });
}
function cancelAddMember() {
  newMember.value = { name: "", role: "", department: "Fintech事業部" };
  isAddDialogOpen.value = false;
}
</script>

<template>
  <main class="content members-page">
    <AppPageHeader
      eyebrow="PEOPLE DIRECTORY"
      title="メンバー"
      description="メンバーの経験と推薦のための情報を管理します。"
    >
      <template #actions
        ><UButton
          icon="i-lucide-plus"
          label="メンバーを追加"
          @click="isAddDialogOpen = true"
      /></template>
    </AppPageHeader>
    <section class="member-summary" aria-label="メンバー集計">
      <div>
        <span>登録メンバー</span
        ><strong>{{ members.length }}<small>名</small></strong>
      </div>
      <p><b>3</b> 部署を横断して、経験と専門性を確認できます。</p>
    </section>
    <div v-if="completedMember" class="import-result">
      <strong>メンバーを追加しました</strong>
      <p>{{ completedMember }} さんをメンバー一覧に登録しました。</p>
    </div>
    <div class="toolbar member-toolbar">
      <UInput
        v-model="query"
        class="member-search"
        icon="i-lucide-search"
        placeholder="名前、役割、部署で検索"
        aria-label="メンバーを検索"
      /><USelect
        v-model="department"
        class="member-department-select"
        :items="departments"
        aria-label="部署で絞り込む"
      />
      <p class="result-count">
        <b>{{ filteredMembers.length }}</b> 名を表示
      </p>
    </div>
    <section class="panel table-panel member-list">
      <div class="table-head">
        <span>メンバー</span><span>部署</span><span>案件経験</span
        ><span>最終更新</span><span></span>
      </div>
      <NuxtLink
        v-for="member in filteredMembers"
        :key="member.id"
        :to="`/members/${member.id}`"
        class="member-row"
        ><div class="member-info">
          <AppAvatar :initial="member.name[0]" :tone="member.tone" tinted />
          <div>
            <strong>{{ member.name }}</strong
            ><span>{{ member.role }}</span>
          </div>
        </div>
        <span class="member-department">{{ member.department }}</span
        ><span class="project-count"
          ><b>{{ member.projects }}</b> 件</span
        ><span class="updated-at">{{ member.updatedAt }}</span
        ><span class="arrow" aria-hidden="true">→</span></NuxtLink
      >
      <div v-if="filteredMembers.length === 0" class="member-empty">
        <strong>条件に一致するメンバーはいません</strong>
        <p>検索キーワードまたは部署の条件を変更してください。</p>
      </div>
    </section>
  </main>
  <UModal
    v-model:open="isAddDialogOpen"
    title="メンバーを追加"
    description="推薦に必要な基本情報を登録します。"
  >
    <template #body
      ><form class="member-form" @submit.prevent="addMember">
        <UFormField label="氏名" required
          ><UInput
            v-model="newMember.name"
            required
            placeholder="例: 田村 恒一" /></UFormField
        ><UFormField label="役割" required
          ><UInput
            v-model="newMember.role"
            required
            placeholder="例: Product Designer" /></UFormField
        ><UFormField label="部署"
          ><USelect
            v-model="newMember.department"
            :items="departments.slice(1)"
        /></UFormField>
        <AppFormActions>
          <UButton
            label="キャンセル"
            color="neutral"
            variant="outline"
            @click="cancelAddMember"
          /><UButton
            type="submit"
            label="追加する"
            icon="i-lucide-plus"
            :loading="isPending"
          />
        </AppFormActions></form
    ></template>
  </UModal>
</template>
