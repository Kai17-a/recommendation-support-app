# 推薦業務支援システム

推薦業務の情報整理、根拠抽出、推薦文ドラフト作成を支援する業務システムです。
AIは業務上の最終判断、人物評価、スコアリング、ランキングを行いません。

詳細な要件・設計は[designdoc/README.md](designdoc/README.md)を参照してください。

## 構成

| ディレクトリ | 内容 |
|---|---|
| `apps/web` | Nuxt / VueによるWeb UI |
| `apps/api` | FastAPIによるREST API |
| `docker-compose.yml` | PostgreSQL、Redis、MinIOのローカル開発環境 |
| `justfile` | 開発・検証コマンド |
| `mise.toml` | Pythonとjustのツールバージョン定義 |

## 必要なツール

- [mise](https://mise.jdx.dev/)
- Bun
- uv
- Docker DesktopまたはDocker Engine（ローカル基盤を起動する場合）

Python 3.14とjustは`mise.toml`で管理します。シェルでmiseを有効化していない場合も、以下のように`mise exec --`を付ければ実行できます。

```bash
mise install
mise exec -- just --list
```

## 初回セットアップ

```bash
cp .env.example .env
mise exec -- just install
```

`.env`はローカル開発専用です。AI GatewayのAPIキーなど、実際の秘密情報をコミットしないでください。

## ローカル開発

別々のターミナルで次のコマンドを実行します。

```bash
# PostgreSQL、Redis、MinIOを起動する
mise exec -- just infra-up

# DBマイグレーションを適用する
mise exec -- just db-migrate

# APIを起動する: http://localhost:8000
mise exec -- just api-dev

# UIを起動する: http://localhost:3000
mise exec -- just web-dev
```

APIの稼働確認は以下で行えます。

```bash
curl http://localhost:8000/health
```

OpenAPI仕様とSwagger UIは、API起動後に以下で確認できます。

- `http://localhost:8000/openapi.json`
- `http://localhost:8000/docs`

ローカル基盤を停止するには、次を実行します。

```bash
mise exec -- just infra-down
```

## 品質確認

```bash
# lintと型検査
mise exec -- just lint

# 整形を適用
mise exec -- just format

# テスト
mise exec -- just test
```

UIだけを確認する場合は、以下も利用できます。

```bash
bun run web:lint
bun run web:typecheck
bun run web:test
bun run --cwd apps/web build
```
