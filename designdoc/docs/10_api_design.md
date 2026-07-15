# API設計

## 1. 方針

- REST APIを基本とする
- JSONを利用する
- 非同期AI処理はジョブAPIで管理する
- 認可はAPI単位とデータ単位の両方で実施する
- 論理削除済みデータは通常APIでは返さない

## 2. メンバーAPI

```http
GET /api/v1/members
POST /api/v1/members
GET /api/v1/members/{memberId}
PATCH /api/v1/members/{memberId}
DELETE /api/v1/members/{memberId}
POST /api/v1/members/{memberId}/restore
```

## 3. 案件経験API

```http
GET /api/v1/members/{memberId}/projects
POST /api/v1/members/{memberId}/projects
GET /api/v1/projects/{projectId}
PATCH /api/v1/projects/{projectId}
DELETE /api/v1/projects/{projectId}
```

## 4. 案件報告API

```http
GET /api/v1/projects/{projectId}/reports
POST /api/v1/projects/{projectId}/reports
GET /api/v1/reports/{reportId}
PATCH /api/v1/reports/{reportId}
DELETE /api/v1/reports/{reportId}
```

## 5. Markdown取り込みAPI

```http
POST /api/v1/projects/{projectId}/markdown-imports
GET /api/v1/markdown-imports/{importId}
GET /api/v1/markdown-imports/{importId}/warnings
PATCH /api/v1/markdown-import-warnings/{warningId}
```

### リクエスト

`multipart/form-data`

- `member_id`
- `file`
- `retain_file` 任意

`project_id`はURLパスを正とし、フォームでは受け取らない。解析は非同期で実行する。

初期リリースでは、拡張子は`.md`、UTF-8テキスト、最大10 MiBとする。空ファイル、NUL文字を含むファイル、同一メンバー・案件への同一内容の再取り込みは拒否する。`retain_file`の既定値は`false`とし、`true`の場合だけ元本文を保持する。

テンプレートは`designdoc/templates/project_report_template.md`の見出しを正とし、日付はISO 8601、報告種別は`periodic` / `final` / `ad_hoc`とする。警告の解決状態は`unresolved` / `resolved` / `ignored`とする。AI Gatewayが利用できない場合も決定的に抽出できた項目は保存し、警告付き完了とする。

### 受付レスポンス例

```json
{
  "import_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "project_report_id": null,
  "warning_count": 0,
  "extracted_skill_count": 0
}
```

### 完了時の取得レスポンス例

```json
{
  "import_id": "uuid",
  "job_id": "uuid",
  "status": "completed_with_warnings",
  "project_report_id": "uuid",
  "warning_count": 2,
  "extracted_skill_count": 4
}
```

## 6. AI案件分析API

```http
POST /api/v1/projects/{projectId}/analyses
GET /api/v1/ai-jobs/{jobId}
GET /api/v1/ai-analyses/{analysisId}
PATCH /api/v1/ai-analyses/{analysisId}
```

`POST /api/v1/projects/{projectId}/analyses` は `202 Accepted` でAIジョブを返す。

## 7. 人物評価API

```http
GET /api/v1/members/{memberId}/evaluations
POST /api/v1/members/{memberId}/evaluations
PATCH /api/v1/evaluations/{evaluationId}
DELETE /api/v1/evaluations/{evaluationId}
```

## 8. スキルAPI

```http
GET /api/v1/members/{memberId}/skills
POST /api/v1/members/{memberId}/skills
PATCH /api/v1/member-skills/{memberSkillId}
DELETE /api/v1/member-skills/{memberSkillId}
GET /api/v1/member-skills/{memberSkillId}/evidences
```

## 9. 推薦プロジェクトAPI

```http
GET /api/v1/recommendations
POST /api/v1/recommendations
GET /api/v1/recommendations/{recommendationId}
PATCH /api/v1/recommendations/{recommendationId}
DELETE /api/v1/recommendations/{recommendationId}

POST /api/v1/recommendations/{recommendationId}/generate
GET /api/v1/recommendations/{recommendationId}/versions
GET /api/v1/recommendation-versions/{versionId}
PATCH /api/v1/recommendation-versions/{versionId}
POST /api/v1/recommendations/{recommendationId}/finalize
GET /api/v1/recommendation-versions/{versionId}/evidences
```

`POST /api/v1/recommendations/{recommendationId}/generate` は `202 Accepted` でAIジョブを返す。

`PATCH /api/v1/recommendation-versions/{versionId}` は元の版を上書きせず、上司編集版として新しいバージョンを作成して返す。元版に紐付く根拠参照は新しい版へ引き継ぐ。

`POST /api/v1/recommendations/{recommendationId}/finalize` の本文は、上司が確定対象として選択した版を明示する。

```json
{
  "version_id": "uuid"
}
```

## 10. 管理API

```http
GET /api/v1/admin/ai-settings
PATCH /api/v1/admin/ai-settings

GET /api/v1/admin/retention-policies
PATCH /api/v1/admin/retention-policies/{policyId}

GET /api/v1/admin/audit-logs
GET /api/v1/admin/deleted-records
POST /api/v1/admin/deleted-records/{targetType}/{targetId}/restore
POST /api/v1/admin/deleted-records/{targetType}/{targetId}/purge
```

AI設定の更新ではAPIキー本文を受け取らず、Secret参照名のみを更新する。

## 11. エラー形式

```json
{
  "error": {
    "code": "AI_GATEWAY_TIMEOUT",
    "message": "AI処理がタイムアウトしました。",
    "details": {},
    "request_id": "uuid"
  }
}
```

## 12. 主なエラーコード

- `VALIDATION_ERROR`
- `FORBIDDEN`
- `NOT_FOUND`
- `CONFLICT`
- `MARKDOWN_TEMPLATE_UNSUPPORTED`
- `MARKDOWN_PARSE_FAILED`
- `AI_GATEWAY_TIMEOUT`
- `AI_GATEWAY_UNAVAILABLE`
- `AI_OUTPUT_SCHEMA_INVALID`
- `EVIDENCE_NOT_FOUND`
- `PURGE_NOT_ALLOWED`
