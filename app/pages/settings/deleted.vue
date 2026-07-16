<script setup lang="ts">
const restored = ref(false);
</script>
<template>
  <main class="content narrow">
    <AppBackLink to="/settings" label="システム設定に戻る" />
    <p class="eyebrow">DELETED DATA</p>
    <h1>削除済みデータ管理</h1>
    <p class="muted">削除されたデータの復元と物理削除を行います。</p>
    <div v-if="restored" class="import-result">
      <strong>データを復元しました</strong>
      <p>旧案件報告：加盟店管理を案件報告一覧へ戻しました。</p>
    </div>
    <section class="panel table-panel">
      <div
        class="table-head"
        style="grid-template-columns: 1.5fr 1fr 1fr 100px"
      >
        <span>対象</span><span>削除日時</span><span>削除者</span><span></span>
      </div>
      <div
        v-if="!restored"
        class="member-row"
        style="grid-template-columns: 1.5fr 1fr 1fr 100px"
      >
        <span>旧案件報告：加盟店管理</span><span>2026/07/01</span
        ><span>田中 恒一</span
        ><UButton
          label="復元"
          color="primary"
          variant="link"
          @click="restored = true"
        />
      </div>
      <div v-else class="member-empty">
        <strong>削除済みデータはありません</strong>
        <p>復元可能なデータはここに表示されます。</p>
      </div>
    </section>
  </main>
</template>
