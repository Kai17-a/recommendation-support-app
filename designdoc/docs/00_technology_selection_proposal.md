# 技術選定案

## 1. 目的

本書は、推薦業務支援システムの初期リリースに向けた技術選定案である。  
既存の要求・設計・ADRを正とし、実装開始前の確認資料として扱う。

## 2. 技術選定

| 領域 | 採用案 | 設計との適合 |
|---|---|---|
| 構成 | Bun workspace + uv workspaceによるモノレポ | UI・API・契約を分離しつつ、一元管理する。ルートの開発・検証コマンドは`justfile`で統一する。 |
| Web UI | Nuxt.js / Vue.js / TypeScript | 画面設計、アクセシビリティ、長文編集UIに対応する。 |
| API | FastAPI / Python 3.14 / REST | 業務ロジック・認可・AIオーケストレーションをモジュール分割する。Python依存はuvで管理する。 |
| DB | PostgreSQL | UUID、JSON監査ログ、トランザクション、論理削除に適合する。 |
| ORM・Migration | SQLAlchemy 2.x + Alembic | Pythonで型付きのDBアクセスとマイグレーション管理を行う。 |
| 非同期AI処理 | Dramatiq + Redis | `ai_jobs`をDBで正として保持し、実行キューを分離する。SSEで状態を通知する。 |
| AI接続 | httpxによるOpenAI互換HTTP Adapter | AI Gatewayの`base_url`を設定し、特定LLMベンダーへの依存を排除する。 |
| Markdown | markdown-it-py + bleach | Markdown構造を安全に解析し、HTMLを許可する場合はサニタイズする。 |
| ファイル保存 | S3互換ストレージ | 元Markdownを保持する設定時のみ保存する。ローカル開発ではMinIOを利用する。 |
| 認証 | OIDC（企業IdP連携） | 設計の認証方針に準拠する。SAMLはIdP要件確定後に追加検討する。 |
| 秘密情報 | `.env` + sops | APIキー等をDBへ平文保存しない。プロトタイプの復号は開発・デプロイ環境に限定する。 |
| API契約・型 | OpenAPI 3.1 + TypeScript型生成 | PythonとTypeScript間でソースを共用せず、REST API契約を正として型を生成する。 |
| 静的解析・整形（UI） | ESLint + Prettier + vue-tsc | TypeScript・Vueコンポーネントのlint、整形、型検査を行う。 |
| 静的解析・整形（API） | Ruff + ty | Pythonのlint・整形はRuff、型検査はtyで実施する。 |
| テスト | pytest、httpx、Playwright、Testcontainers | ドメイン・API・E2E・PostgreSQL連携を検証する。UI単体テストにはVitestを利用する。 |

## 3. ディレクトリ構成案

```text
apps/web             Nuxt.js UI
apps/api             FastAPI REST API・業務ドメイン・AI Orchestrator
packages/api-client  OpenAPIから生成するTypeScript APIクライアント・型
contracts/openapi    REST API契約
infra                Docker Compose・MinIO・ローカル開発設定
justfile             開発・テスト・CIコマンドの統一入口
```

## 4. AI実装方針

AIは、以下の専門コンポーネントとして分離する。

- Markdown Parser
- Project Analyzer
- Evidence Finder
- Recommendation Generator
- Warning Generator

AI Gateway呼び出しはAdapter層に限定する。AIは推薦可否・人物評価・スコアリング・ランキングを扱わない。

Markdownの構文・見出し解析、拡張子検証、サイズ検証、バイナリ判定はアプリケーション側で決定的に実施する。AI Gatewayには、曖昧な内容の構造化、根拠抽出、警告生成のみを依頼する。

## 5. 認証・認可

OIDCによる企業IdP連携と、操作者のロールおよび部署に基づく認可を実装対象とする。監査ログもAPI設計および要求定義との整合のため実装対象とする。

## 6. 実装開始前の確認事項

- IdP固有のクライアント設定は導入環境で決定する。APIは標準OIDC Discovery/JWKSに対応する。
- AI Gateway設定の保存モデル。秘密情報はSecret Manager参照名のみをDBへ保存する案とする。
  - `ai_settings`へ接続先、モデル、Secret参照名、タイムアウト、リトライ、プロンプトバージョンを保存する。APIキー本文は`.env`またはsopsで管理し、DBには保存しない。
- Markdown Parserは「構造解析は決定的パーサー、曖昧箇所の抽出補助はAI」の二層構成とする。
- 各ステータス・Enumの正式な値、および確定済み推薦文の編集可否。
- 部長・マネージャーが閲覧できる監査ログの対象範囲。
