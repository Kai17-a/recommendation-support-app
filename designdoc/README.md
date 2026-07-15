# 推薦業務支援システム

## 概要

本システムは、**推薦業務という業務プロセスをデジタル化し、その一部をAIで支援するシステム**である。

初期版は**閉じた社内ネットワークで利用するプロトタイプ**を想定します。インターネット公開や不特定多数への提供は対象外とし、セキュリティ要件は検証に必要な最小限に留めます。

AIは推薦の可否を判断せず、以下を支援する。

- Markdown形式の案件報告の解析
- 案件経験・人物評価・スキル情報の整理
- 推薦目的に応じた根拠の抽出
- 推薦文ドラフトの作成
- 根拠不足や情報の曖昧さに関する警告

## 基本方針

- 業務の自動化ではなく、業務負荷の軽減を目的とする
- AI出力には必ず根拠を紐付ける
- AIによるスコアリング、ランキング、推薦可否判定は行わない
- AI処理はAI Gateway経由で実行する
- AI GatewayはOpenAI互換APIを提供し、Custom Providerとして接続する
- 接続情報は `.env` で管理する
- `.env` はGitへコミットしない

## ドキュメント構成

| ディレクトリ | 内容 |
|---|---|
| `docs/` | 要求、設計、ユースケース、DB、AI、画面、API、セキュリティ |
| `adr/` | 主要な設計判断と理由 |
| `templates/` | Markdown入力テンプレート |

## 主要ドキュメント

1. [システム概要](docs/01_system_overview.md)
2. [要求定義](docs/02_requirements.md)
3. [業務フロー](docs/03_business_flow.md)
4. [ユースケース](docs/04_use_cases.md)
5. [UMLユースケース図](docs/05_usecase_diagram.md)
6. [ER図](docs/06_er_diagram.md)
7. [データベース設計](docs/07_database_design.md)
8. [AIアーキテクチャ](docs/08_ai_architecture.md)
9. [画面設計](docs/09_screen_design.md)
10. [API設計](docs/10_api_design.md)
11. [セキュリティ](docs/11_security.md)
12. [非機能要件](docs/12_non_functional_requirements.md)
13. [用語集](docs/13_glossary.md)
14. [将来機能](docs/14_future_features.md)
