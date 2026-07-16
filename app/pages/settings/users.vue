<script setup lang="ts">
const isFormOpen = ref(false);
const completed = ref(false);
const completedEmail = ref("");
const invite = ref({ name: "", email: "", department: "Fintech事業部" });
const users = ref([
  {
    name: "田中 恒一",
    email: "manager@acme.co.jp",
    department: "Fintech事業部",
    role: "部長・マネージャー",
    initial: "田",
  },
  {
    name: "伊藤 遼",
    email: "ito@acme.co.jp",
    department: "Platform部",
    role: "メンバー",
    initial: "伊",
  },
]);
const departmentOptions = ["Fintech事業部", "Platform部", "新規事業部"];
const { isPending, run } = useMockAction();
async function sendInvite() {
  const submittedInvite = { ...invite.value };
  await run(() => {
    users.value.push({
      ...submittedInvite,
      role: "メンバー",
      initial: submittedInvite.name[0],
    });
    completedEmail.value = submittedInvite.email;
    invite.value = { name: "", email: "", department: "Fintech事業部" };
    isFormOpen.value = false;
    completed.value = true;
  });
}
function cancelInvite() {
  invite.value = { name: "", email: "", department: "Fintech事業部" };
  isFormOpen.value = false;
}
</script>
<template>
  <main class="content">
    <AppPageHeader
      eyebrow="ADMINISTRATION"
      title="ユーザー・部署管理"
      description="ユーザーの権限と所属部署を管理します。"
    >
      <template #actions
        ><UButton
          icon="i-lucide-user-plus"
          label="ユーザーを招待"
          @click="isFormOpen = !isFormOpen"
      /></template>
    </AppPageHeader>
    <form
      v-if="isFormOpen"
      class="panel form-panel"
      @submit.prevent="sendInvite"
    >
      <UFormField label="氏名" required>
        <UInput v-model="invite.name" required placeholder="例: 佐々木 亮" />
      </UFormField>
      <UFormField label="メールアドレス" required>
        <UInput
          v-model="invite.email"
          type="email"
          required
          placeholder="name@acme.co.jp"
        />
      </UFormField>
      <UFormField label="所属部署">
        <USelect v-model="invite.department" :items="departmentOptions" />
      </UFormField>
      <AppFormActions>
        <UButton
          label="キャンセル"
          color="neutral"
          variant="outline"
          @click="cancelInvite"
        /><UButton type="submit" label="招待を送信" :loading="isPending" />
      </AppFormActions>
    </form>
    <div v-if="completed" class="import-result">
      <strong>招待を送信しました</strong>
      <p>{{ completedEmail }} にワークスペースへの招待を送信しました。</p>
    </div>
    <section class="panel table-panel">
      <div class="table-head">
        <span>ユーザー</span><span>部署</span><span>権限</span><span>状態</span
        ><span></span>
      </div>
      <div v-for="user in users" :key="user.email" class="member-row">
        <div class="member-info">
          <AppAvatar :initial="user.initial" tinted />
          <div>
            <strong>{{ user.name }}</strong
            ><span>{{ user.email }}</span>
          </div>
        </div>
        <span>{{ user.department }}</span
        ><span>{{ user.role }}</span
        ><AppStatus tone="green">有効</AppStatus><span>→</span>
      </div>
    </section>
  </main>
</template>
