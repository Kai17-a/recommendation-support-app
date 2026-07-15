# 技術選定案

## 1. 目的

本書は、推薦業務支援システムの初期リリースに向けた技術選定案である。  
既存の要求・設計・ADRを正とし、実装開始前の確認資料として扱う。

## 2. 技術選定

| 領域           | 採用案                                               | 設計との適合                                                                |
| -------------- | ---------------------------------------------------- | --------------------------------------------------------------------------- |
| 構成           | bun モノレポ                                         | UI・API・共有型を分離しつつ一元管理する。                                   |
| Web UI         | Nuxt.js / Vue.js / TypeScript                        | 画面設計、アクセシビリティ、長文編集UIに対応する。                          |
| API            | fastapi / Python3.14 / REST / uv, ruff, ty           | 業務ロジック・認可・AIオーケストレーションをモジュール分割する。            |
| DB             | PostgreSQL                                           | UUID、JSON監査ログ、トランザクション、論理削除に適合する。                  |
| ORM・Migration | Prisma                                               | 型安全なDBアクセスとマイグレーション管理を提供する。                        |
| 非同期AI処理   | BullMQ + Redis                                       | `ai_jobs` をDBで正として保持し、実行キューを分離する。SSEで状態を通知する。 |
| AI接続         | OpenAI互換HTTP Adapter                               | AI Gatewayの`base_url`を設定し、特定LLMベンダーへの依存を排除する。         |
| Markdown       | remark系パーサー                                     | Markdown構造・拡張子・サイズ・バイナリを安全に検証する。                    |
| ファイル保存   | S3互換ストレージ                                     | 元Markdownを保持する設定時のみ保存する。ローカル開発ではMinIOを利用する。   |
| 認証           | OIDC（企業IdP連携）                                  | 設計の認証方針に準拠する。SAMLはIdP要件確定後に追加検討する。               |
| 秘密情報       | .env / sops                                          | APIキー等をDBへ平文保存しない。                                             |
| テスト         | Vitest、pytest,Supertest、Playwright、Testcontainers | ドメイン・API・E2E・PostgreSQL連携を検証する。                              |

## 3. ディレクトリ構成案

```text
apps/web        Nuxt.js UI
apps/api        fastapi REST API
packages/domain 業務ルール・エンティティ・値オブジェクト
packages/ai     Orchestrator / 専門AIサービス / Gateway Adapter
packages/shared API契約・Enum・共通型
```

## 4. AI実装方針

AIは、以下の専門コンポーネントとして分離する。

- Markdown Parser
- Project Analyzer
- Evidence Finder
- Recommendation Generator
- Warning Generator

AI Gateway呼び出しはAdapter層に限定する。AIは推薦可否・人物評価・スコアリング・ランキングを扱わない。

## 5. 実装開始前の確認事項

- IdPの具体的な選定と、OIDCを正式採用してよいか。
  - 現時点では不要
- AI Gateway設定の保存モデル。秘密情報はSecret Manager参照名のみをDBへ保存する案とする。
  - 現時点では不要。プロトタイプでは.envにsopsを利用する
- Markdown Parserを「構造解析は決定的パーサー、曖昧箇所の抽出補助はAI」と二層化してよいか。現行設計にはAI Gateway経由解析と専門コンポーネントの両表現がある。
- `ai_settings`およびプロンプト設定のテーブル定義がER図にない点。
- 各ステータス・Enumの正式な値、および確定済み推薦文の編集可否。
- 部長・マネージャーが閲覧できる監査ログの対象範囲。
