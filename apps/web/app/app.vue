<script setup lang="ts">
import type {
  AiJob,
  AiSetting,
  AiSettingUpdate,
  MarkdownImport,
  Member,
  Project,
  Recommendation,
  RecommendationVersion,
} from "./types/api";
import { ApiError, createApiClient } from "./utils/api-client";
import { initializeOidc } from "./utils/oidc";
import { tokenStore } from "./utils/token-store";

type View = "members" | "member" | "recommendations" | "admin";
const config = useRuntimeConfig();
const api = createApiClient({
  baseUrl: config.public.apiBase,
  getToken: tokenStore.get,
});
const authenticated = ref(false);
const oidcError = ref("");
const view = ref<View>("members");
const members = ref<Member[]>([]);
const selectedMember = ref<Member | null>(null);
const projects = ref<Project[]>([]);
const recommendations = ref<Recommendation[]>([]);
const selectedRecommendation = ref<Recommendation | null>(null);
const versions = ref<RecommendationVersion[]>([]);
const selectedVersionId = ref("");
const job = ref<AiJob | null>(null);
const importResult = ref<MarkdownImport | null>(null);
const loading = ref(false);
const error = ref("");
const purpose = ref("");
const targetName = ref("");
const markdownFile = ref<File | null>(null);
const retainFile = ref(false);
const aiSetting = ref<AiSetting | null>(null);
const aiSettingForm = reactive<AiSettingUpdate>({
  provider: "custom",
  base_url: "",
  model: "",
  api_key_secret_ref: "AI_GATEWAY_API_KEY",
  timeout_seconds: 60,
  max_retries: 2,
  prompt_version: "v1",
});

onMounted(() => {
  void initializeLogin();
});

async function initializeLogin() {
  try {
    const oidc = await initializeOidc({
      url: config.public.oidcUrl,
      realm: config.public.oidcRealm,
      clientId: config.public.oidcClientId,
    });
    tokenStore.bind(oidc);
    authenticated.value = oidc.authenticated === true;
    if (authenticated.value) {
      window.setInterval(() => void oidc.updateToken(30), 20_000);
      await loadMembers();
    }
  } catch {
    oidcError.value = "認証サービスへ接続できません。Keycloakの起動を確認してください。";
  }
}

function message(reason: unknown): string {
  if (reason instanceof ApiError) return reason.message;
  return "処理に失敗しました。時間をおいて再試行してください。";
}

async function run(action: () => Promise<void>) {
  loading.value = true;
  error.value = "";
  try {
    await action();
  } catch (reason) {
    error.value = message(reason);
  } finally {
    loading.value = false;
  }
}

async function login() {
  const oidc = await initializeOidc({
    url: config.public.oidcUrl,
    realm: config.public.oidcRealm,
    clientId: config.public.oidcClientId,
  });
  await oidc.login();
}

async function logout() {
  const oidc = await initializeOidc({
    url: config.public.oidcUrl,
    realm: config.public.oidcRealm,
    clientId: config.public.oidcClientId,
  });
  await oidc.logout({ redirectUri: window.location.origin });
  tokenStore.clear();
  authenticated.value = false;
  members.value = [];
  selectedMember.value = null;
}

async function loadMembers() {
  await run(async () => {
    members.value = await api.get<Member[]>("/api/v1/members");
    view.value = "members";
  });
}

async function openAdmin() {
  view.value = "admin";
  await run(loadAiSetting);
}

async function loadAiSetting() {
  try {
    const setting = await api.get<AiSetting>("/api/v1/admin/ai-settings");
    aiSetting.value = setting;
    Object.assign(aiSettingForm, {
      provider: setting.provider,
      base_url: setting.base_url,
      model: setting.model,
      api_key_secret_ref: setting.api_key_secret_ref,
      timeout_seconds: setting.timeout_seconds,
      max_retries: setting.max_retries,
      prompt_version: setting.prompt_version,
    });
  } catch (reason) {
    if (reason instanceof ApiError && reason.status === 404) return;
    throw reason;
  }
}

async function saveAiSetting() {
  await run(async () => {
    aiSetting.value = await api.patch<AiSetting>(
      "/api/v1/admin/ai-settings",
      aiSettingForm,
    );
  });
}

async function openMember(member: Member) {
  await run(async () => {
    selectedMember.value = member;
    projects.value = await api.get<Project[]>(
      `/api/v1/members/${member.id}/projects`,
    );
    view.value = "member";
  });
}

async function importMarkdown(projectId: string) {
  if (!selectedMember.value || !markdownFile.value) return;
  await run(async () => {
    const form = new FormData();
    form.set("member_id", selectedMember.value!.id);
    form.set("retain_file", String(retainFile.value));
    form.set("file", markdownFile.value!);
    importResult.value = await api.post<MarkdownImport>(
      `/api/v1/projects/${projectId}/markdown-imports`,
      form,
    );
    job.value = await api.get<AiJob>(
      `/api/v1/ai-jobs/${importResult.value.job_id}`,
    );
  });
}

async function refreshJob() {
  if (!job.value) return;
  await run(async () => {
    job.value = await api.get<AiJob>(`/api/v1/ai-jobs/${job.value!.id}`);
    if (importResult.value) {
      importResult.value = await api.get<MarkdownImport>(
        `/api/v1/markdown-imports/${importResult.value.import_id}`,
      );
    }
  });
}

async function loadRecommendations() {
  await run(async () => {
    recommendations.value = await api.get<Recommendation[]>(
      "/api/v1/recommendations",
    );
    view.value = "recommendations";
  });
}

async function createRecommendation() {
  if (!selectedMember.value || !purpose.value.trim()) return;
  await run(async () => {
    selectedRecommendation.value = await api.post<Recommendation>(
      "/api/v1/recommendations",
      {
        member_id: selectedMember.value!.id,
        purpose: purpose.value,
        target_name: targetName.value || null,
      },
    );
    recommendations.value = await api.get<Recommendation[]>(
      "/api/v1/recommendations",
    );
    await openRecommendation(selectedRecommendation.value);
  });
}

async function openRecommendation(recommendation: Recommendation) {
  await run(async () => {
    selectedRecommendation.value = recommendation;
    versions.value = await api.get<RecommendationVersion[]>(
      `/api/v1/recommendations/${recommendation.id}/versions`,
    );
    selectedVersionId.value = versions.value.at(-1)?.id ?? "";
    view.value = "recommendations";
  });
}

async function generateRecommendation() {
  if (!selectedRecommendation.value) return;
  await run(async () => {
    job.value = await api.post<AiJob>(
      `/api/v1/recommendations/${selectedRecommendation.value!.id}/generate`,
      {},
    );
  });
}

async function finalizeRecommendation() {
  if (!selectedRecommendation.value || !selectedVersionId.value) return;
  await run(async () => {
    selectedRecommendation.value = await api.post<Recommendation>(
      `/api/v1/recommendations/${selectedRecommendation.value!.id}/finalize`,
      { version_id: selectedVersionId.value },
    );
  });
}
</script>

<template>
  <div class="shell">
    <header>
      <div>
        <span class="eyebrow">Recommendation Support</span>
        <h1>推薦業務支援</h1>
      </div>
      <button v-if="authenticated" class="quiet" type="button" @click="logout">
        ログアウト
      </button>
    </header>

    <main v-if="!authenticated" class="login" aria-labelledby="login-title">
      <section class="card">
        <p class="eyebrow">OIDC session</p>
        <h2 id="login-title">開発用Keycloakでログイン</h2>
        <p>
          ローカルDockerで起動したKeycloakへ移動します。アクセストークンを手入力する必要は
          ありません。
        </p>
        <p v-if="oidcError" class="error" role="alert">{{ oidcError }}</p>
        <button type="button" @click="login">Keycloakでログイン</button>
        <p class="hint">
          開発ユーザー: <code>operator</code> または <code>manager</code> ／ パスワード:
          <code>local-dev-password</code>
        </p>
      </section>
    </main>

    <template v-else>
      <nav aria-label="主要ナビゲーション">
        <button type="button" @click="loadMembers">メンバー</button>
        <button type="button" @click="loadRecommendations">推薦文</button>
        <button type="button" @click="openAdmin">管理</button>
      </nav>
      <p v-if="loading" class="notice" role="status">読み込み中です…</p>
      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <main>
        <section v-if="view === 'members'" aria-labelledby="members-title">
          <div class="section-title">
            <div>
              <p class="eyebrow">People</p>
              <h2 id="members-title">メンバー一覧</h2>
            </div>
            <span>{{ members.length }}名</span>
          </div>
          <div class="grid">
            <button
              v-for="member in members"
              :key="member.id"
              class="member-card"
              type="button"
              @click="openMember(member)"
            >
              <span class="avatar" aria-hidden="true">{{
                member.name.slice(0, 1)
              }}</span>
              <span
                ><strong>{{ member.name }}</strong
                ><small
                  >{{ member.status }} ·
                  {{ member.department_id.slice(0, 8) }}</small
                ></span
              >
              <span aria-hidden="true">→</span>
            </button>
          </div>
          <p v-if="!members.length && !loading" class="empty">
            参照可能なメンバーはいません。
          </p>
        </section>

        <section
          v-else-if="view === 'member' && selectedMember"
          aria-labelledby="member-title"
        >
          <button class="back" type="button" @click="view = 'members'">
            ← 一覧へ
          </button>
          <p class="eyebrow">Member detail</p>
          <h2 id="member-title">{{ selectedMember.name }}</h2>
          <div class="two-column">
            <article class="card">
              <h3>案件経験</h3>
              <div
                v-for="project in projects"
                :key="project.id"
                class="project"
              >
                <div>
                  <strong>{{ project.project_name }}</strong>
                  <p>
                    {{ project.customer_name || "顧客名未設定" }} ·
                    {{ project.status }}
                  </p>
                </div>
                <details>
                  <summary>Markdownを取り込む</summary>
                  <label
                    >Markdownファイル<input
                      type="file"
                      accept=".md,text/markdown"
                      @change="
                        markdownFile =
                          ($event.target as HTMLInputElement).files?.[0] ?? null
                      "
                  ></label>
                  <label class="check"
                    ><input v-model="retainFile" type="checkbox" >
                    原本を保持する</label
                  >
                  <button
                    type="button"
                    :disabled="!markdownFile || loading"
                    @click="importMarkdown(project.id)"
                  >
                    非同期取り込みを開始
                  </button>
                </details>
              </div>
              <p v-if="!projects.length" class="empty">
                案件経験はありません。
              </p>
            </article>
            <article class="card">
              <h3>推薦プロジェクト作成</h3>
              <label>推薦目的<input v-model="purpose" required ></label>
              <label>推薦先<input v-model="targetName" ></label>
              <button
                type="button"
                :disabled="!purpose.trim() || loading"
                @click="createRecommendation"
              >
                作成する
              </button>
              <p class="hint">
                AIは推薦可否を判断せず、根拠付きの文案作成だけを支援します。
              </p>
            </article>
          </div>
          <article v-if="importResult" class="card result" aria-live="polite">
            <h3>取り込み状況</h3>
            <p>
              <span class="status">{{ importResult.status }}</span> 警告
              {{ importResult.warning_count }}件 · スキル候補
              {{ importResult.extracted_skill_count }}件
            </p>
            <button type="button" @click="refreshJob">状態を更新</button>
          </article>
        </section>

        <section
          v-else-if="view === 'recommendations'"
          aria-labelledby="recommendations-title"
        >
          <p class="eyebrow">Human-reviewed drafts</p>
          <h2 id="recommendations-title">推薦文レビュー</h2>
          <div class="review-layout">
            <aside class="card">
              <h3>推薦プロジェクト</h3>
              <button
                v-for="item in recommendations"
                :key="item.id"
                class="list-button"
                type="button"
                @click="openRecommendation(item)"
              >
                <strong>{{ item.purpose }}</strong
                ><small
                  >{{ item.target_name || "推薦先未設定" }} ·
                  {{ item.status }}</small
                >
              </button>
            </aside>
            <article class="card editor">
              <template v-if="selectedRecommendation"
                ><div class="section-title">
                  <h3>{{ selectedRecommendation.purpose }}</h3>
                  <span class="status">{{
                    selectedRecommendation.status
                  }}</span>
                </div>
                <label
                  >表示・確定する版<select v-model="selectedVersionId">
                    <option value="">版を選択</option>
                    <option
                      v-for="version in versions"
                      :key="version.id"
                      :value="version.id"
                    >
                      v{{ version.version_no }} · {{ version.version_type }}
                    </option>
                  </select></label
                >
                <div
                  v-for="version in versions.filter(
                    (item) => item.id === selectedVersionId,
                  )"
                  :key="version.id"
                  class="draft"
                >
                  {{ version.content }}
                </div>
                <div class="actions">
                  <button type="button" @click="generateRecommendation">
                    根拠付き文案を生成</button
                  ><button
                    class="secondary"
                    type="button"
                    :disabled="!selectedVersionId"
                    @click="finalizeRecommendation"
                  >
                    選択版を最終確定
                  </button>
                </div>
                <p class="hint">
                  確定対象の版は上司が明示して選択します。スコアやランキングは使用しません。
                </p></template
              >
              <p v-else class="empty">
                左から推薦プロジェクトを選択してください。
              </p>
            </article>
            <aside class="card">
              <h3>AIジョブ</h3>
              <template v-if="job"
                ><p class="status">{{ job.status }}</p>
                <p>{{ job.job_type }}</p>
                <p v-if="job.error_message" class="error">
                  {{ job.error_message }}
                </p>
                <button type="button" @click="refreshJob">
                  状態を更新
                </button></template
              >
              <p v-else class="empty">実行中のジョブはありません。</p>
            </aside>
          </div>
        </section>

        <section v-else aria-labelledby="admin-title">
          <p class="eyebrow">System operations</p>
          <h2 id="admin-title">管理</h2>
          <div class="two-column">
            <article class="card">
              <h3>AI Gateway設定</h3>
              <p class="hint">
                OpenAI互換のAI Gatewayだけを設定します。APIキー本文は保存せず、環境変数の参照名だけを指定します。
              </p>
              <label>Gateway URL<input v-model="aiSettingForm.base_url" type="url" placeholder="https://gateway.example.com/v1" ></label>
              <label>モデル<input v-model="aiSettingForm.model" placeholder="gpt-4.1-mini" ></label>
              <label>APIキーのSecret参照名<input v-model="aiSettingForm.api_key_secret_ref" placeholder="AI_GATEWAY_API_KEY" ></label>
              <label>タイムアウト（秒）<input v-model.number="aiSettingForm.timeout_seconds" type="number" min="1" max="600" ></label>
              <label>最大再試行回数<input v-model.number="aiSettingForm.max_retries" type="number" min="0" max="10" ></label>
              <label>プロンプト版<input v-model="aiSettingForm.prompt_version" placeholder="v1" ></label>
              <button type="button" :disabled="loading || !aiSettingForm.base_url || !aiSettingForm.model || !aiSettingForm.api_key_secret_ref || !aiSettingForm.prompt_version" @click="saveAiSetting">AI設定を保存</button>
              <p v-if="aiSetting" class="hint">最終更新: {{ new Date(aiSetting.updated_at).toLocaleString("ja-JP") }}</p>
            </article>
            <div class="grid">
            <a
              class="card admin-link"
              :href="`${config.public.apiBase}/docs#/admin`"
              target="_blank"
              rel="noopener"
              ><strong>監査ログ・削除済みデータ</strong
              ><span>管理APIドキュメントを開く ↗</span></a
            ><a
              class="card admin-link"
              :href="`${config.public.apiBase}/docs#/admin/get_ai_settings_api_v1_admin_ai_settings_get`"
              target="_blank"
              rel="noopener"
              ><strong>AI Gateway設定</strong
              ><span>Secret参照名と接続設定を管理 ↗</span></a
            >
            </div>
          </div>
          <p class="hint">管理APIはsystem_operatorロールだけが利用できます。</p>
        </section>
      </main>
    </template>
  </div>
</template>

<style>
:root {
  font-family: Inter, "Noto Sans JP", system-ui, sans-serif;
  color: #17211b;
  background: #f3f5ef;
  font-synthesis: none;
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
}
.shell {
  min-height: 100vh;
}
header {
  height: 78px;
  padding: 0 max(24px, calc((100vw - 1240px) / 2));
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #173e31;
  color: white;
}
h1 {
  font-size: 1.25rem;
  margin: 2px 0;
}
h2 {
  font-size: clamp(1.7rem, 4vw, 2.5rem);
  margin: 0.25rem 0 1.5rem;
}
h3 {
  margin-top: 0;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.7rem;
  font-weight: 700;
  color: #89b7a3;
}
nav {
  padding: 12px max(24px, calc((100vw - 1240px) / 2));
  display: flex;
  gap: 8px;
  border-bottom: 1px solid #dce2da;
  background: white;
}
main {
  max-width: 1240px;
  margin: auto;
  padding: 42px 24px;
}
.login {
  display: grid;
  place-items: center;
  min-height: calc(100vh - 78px);
}
.login .card {
  max-width: 520px;
}
.card {
  background: white;
  border: 1px solid #dce2da;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 8px 30px #173e310c;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 14px;
}
.member-card {
  display: flex;
  align-items: center;
  gap: 14px;
  text-align: left;
  background: white;
  color: inherit;
  border: 1px solid #dce2da;
  border-radius: 12px;
  padding: 17px;
}
.member-card span:nth-child(2) {
  display: grid;
  gap: 4px;
  flex: 1;
}
.avatar {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #dff0e7;
  color: #173e31;
  font-weight: 800;
}
small,
.hint,
.empty {
  color: #67746c;
}
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.two-column {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 18px;
}
.project {
  padding: 16px 0;
  border-top: 1px solid #e8ebe7;
}
.project p {
  margin: 0.35rem 0;
}
details {
  margin-top: 12px;
}
summary {
  cursor: pointer;
  font-weight: 700;
}
label {
  display: grid;
  gap: 7px;
  margin: 16px 0;
  font-weight: 650;
}
input,
select {
  width: 100%;
  padding: 11px;
  border: 1px solid #aeb9b2;
  border-radius: 7px;
  font: inherit;
}
.check {
  display: flex;
  align-items: center;
}
.check input {
  width: auto;
}
button {
  padding: 10px 15px;
  border: 0;
  border-radius: 7px;
  background: #21674f;
  color: white;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}
button:hover {
  background: #184c3b;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.quiet,
.back {
  background: transparent;
}
.secondary {
  background: #bf6a35;
}
.notice,
.error {
  max-width: 1240px;
  margin: 14px auto;
  padding: 12px 24px;
}
.error {
  color: #8b2424;
  background: #fff0f0;
}
.result {
  margin-top: 18px;
}
.status {
  display: inline-block;
  padding: 4px 9px;
  border-radius: 99px;
  background: #e4eee8;
  color: #24523f;
  font-weight: 700;
}
.review-layout {
  display: grid;
  grid-template-columns: 260px minmax(360px, 1fr) 230px;
  gap: 16px;
}
.list-button {
  width: 100%;
  display: grid;
  gap: 5px;
  text-align: left;
  margin-bottom: 8px;
  background: #f1f5f1;
  color: #173e31;
}
.editor {
  min-height: 430px;
}
.draft {
  white-space: pre-wrap;
  line-height: 1.8;
  border: 1px solid #dce2da;
  border-radius: 8px;
  padding: 18px;
  margin: 15px 0;
  background: #fbfcfa;
}
.actions {
  display: flex;
  gap: 10px;
}
.admin-link {
  display: grid;
  gap: 12px;
  color: inherit;
  text-decoration: none;
}
.admin-link:hover {
  border-color: #21674f;
}
@media (max-width: 800px) {
  .two-column,
  .review-layout {
    grid-template-columns: 1fr;
  }
  header {
    padding: 0 18px;
  }
  main {
    padding: 28px 18px;
  }
  nav {
    overflow: auto;
    padding-inline: 18px;
  }
}
</style>
