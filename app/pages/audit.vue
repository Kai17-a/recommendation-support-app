<template>
  <main class="content">
    <AppPageHeader
      eyebrow="AUDIT LOG"
      title="監査ログ"
      description="ワークスペースで行われた変更の履歴です。"
      ><template #actions
        ><button class="filter">期間：過去30日　⌄</button></template
      ></AppPageHeader
    >
    <section class="panel table-panel">
      <div
        class="table-head"
        style="grid-template-columns: 1.3fr 1.4fr 1fr 1fr"
      >
        <span>日時</span><span>操作者</span><span>操作</span><span>対象</span>
      </div>
      <div
        class="member-row"
        style="grid-template-columns: 1.3fr 1.4fr 1fr 1fr"
      >
        <span>2026/07/16 09:42</span><span>田中 恒一</span
        ><span>推薦文を生成</span><span>鈴木 恒一</span>
      </div>
      <div
        class="member-row"
        style="grid-template-columns: 1.3fr 1.4fr 1fr 1fr"
      >
        <span>2026/07/16 08:15</span><span>田中 恒一</span
        ><span>案件報告を更新</span><span>決済プロダクト</span>
      </div>
    </section>
  </main>
</template>
