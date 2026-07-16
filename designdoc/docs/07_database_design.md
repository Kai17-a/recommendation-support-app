# データベース設計

## 1. 前提

- RDBMSを前提とする
- 主キーはUUIDを推奨する
- 日時はUTCで保存し、表示時に利用者のタイムゾーンへ変換する
- 業務データは原則論理削除する
- 監査ログは共通テーブルで管理する
- `source_type + source_id` によるポリモーフィック関連はアプリケーション側で整合性を保証する

## 2. 主要テーブル

### departments

部署階層を管理する。

| カラム     | 型        | 必須 | 説明       |
| ---------- | --------- | ---: | ---------- |
| id         | uuid      |  Yes | 主キー     |
| parent_id  | uuid      |   No | 親部署     |
| name       | varchar   |  Yes | 部署名     |
| code       | varchar   |  Yes | 部署コード |
| created_at | timestamp |  Yes | 作成日時   |
| updated_at | timestamp |  Yes | 更新日時   |

### users

システム利用者を管理する。

| カラム        | 型      | 必須 | 説明                      |
| ------------- | ------- | ---: | ------------------------- |
| id            | uuid    |  Yes | 主キー                    |
| department_id | uuid    |  Yes | 所属部署                  |
| name          | varchar |  Yes | 氏名                      |
| email         | varchar |  Yes | ログイン識別子            |
| role          | enum    |  Yes | manager / system_operator |
| status        | enum    |  Yes | active / inactive         |

### members

推薦対象となるメンバーを管理する。

| カラム          | 型        | 必須 | 説明                        |
| --------------- | --------- | ---: | --------------------------- |
| id              | uuid      |  Yes | 主キー                      |
| department_id   | uuid      |  Yes | 所属部署                    |
| manager_user_id | uuid      |  Yes | 管理上司                    |
| name            | varchar   |  Yes | 氏名                        |
| status          | enum      |  Yes | active / inactive / retired |
| deleted_at      | timestamp |   No | 論理削除日時                |
| deleted_by      | uuid      |   No | 削除者                      |

### project_experiences

メンバー単位の案件経験を管理する。

### project_reports

定期報告、終了報告、任意報告を時系列で管理する。

### member_evaluations

人物評価を時系列で管理する。

### skills / member_skills

スキルマスタとメンバー保有スキルを管理する。  
`member_skills.status` は以下を想定する。

- `ai_extracted`
- `manager_confirmed`
- `rejected`

### markdown_imports

Markdown取り込みの実行履歴を管理する。

### recommendations / recommendation_versions

推薦プロジェクトと推薦文のバージョンを管理する。

### ai_jobs / ai_analyses

AI処理状態とAI出力を分離して管理する。

### audit_logs

すべての主要な変更履歴を共通形式で保持する。

## 3. 推奨インデックス

- `users(email)` UNIQUE
- `departments(code)` UNIQUE
- `members(department_id, deleted_at)`
- `members(manager_user_id, deleted_at)`
- `project_experiences(member_id, period_from, deleted_at)`
- `project_reports(project_experience_id, report_date, deleted_at)`
- `member_evaluations(member_id, evaluation_date, deleted_at)`
- `member_skills(member_id, status, deleted_at)`
- `recommendations(member_id, status, deleted_at)`
- `recommendation_versions(recommendation_id, version_no)` UNIQUE
- `markdown_imports(content_hash, member_id, project_experience_id)`
- `ai_jobs(status, created_at)`
- `audit_logs(target_type, target_id, changed_at)`
- `audit_logs(changed_by, changed_at)`

## 4. 論理削除

通常検索では `deleted_at IS NULL` を必須条件とする。  
親レコードを論理削除しても子レコードは物理削除しない。

復元時は以下を選択可能とする。

- 親のみ復元
- 関連レコードも一括復元

## 5. 監査ログ

`audit_logs` はアプリケーションサービス層またはDBトランザクション境界で自動生成する。

記録対象:

- create
- update
- delete
- restore
- import
- finalize
- settings_change
- purge

## 6. 物理削除

物理削除前に削除対象のスナップショット要約を監査ログへ保存する。  
個人情報保護上、物理削除後に元データ全文を監査ログへ残さない設定も可能にする。
