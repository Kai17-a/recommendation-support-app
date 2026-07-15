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

## Dockerを使ったローカル起動

通常のローカル開発では、PostgreSQL、Redis、MinIO、KeycloakをDocker Composeで起動し、
API、非同期worker、Web UIはホスト上で起動します。`compose.production.yml`は本番構成例、
`docker-compose.integration.yml`は自動結合試験専用なので、通常開発では直接使用しません。

### 1. 設定と依存関係の準備

```bash
cp .env.example .env
mise install
mise exec -- just install
```

`.env`の既定値はローカルComposeのPostgreSQL、Redis、MinIO、Keycloakへ接続する設定です。
本番IdPへ接続する場合だけ、`OIDC_ISSUER_URL`、`OIDC_AUDIENCE`、
`NUXT_PUBLIC_OIDC_*`を企業IdPの設定値へ置き換えてください。

AI機能を使う場合は、管理APIのAI設定に保存するSecret参照名と同名の環境変数へ、
AI Gatewayのキーを設定します。キー自体をAI設定APIやDBへ保存しないでください。
`operator`でWeb UIの「管理」を開くと、AI Gatewayの接続設定とSecret参照名を更新できます。

### 2. Docker基盤の起動

```bash
docker compose up -d
docker compose ps
```

`postgres`、`redis`、`keycloak`が`healthy`、`minio`が`Up`、`minio-init`が正常終了すれば準備完了です。

| サービス | ローカルURL・ポート |
|---|---|
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |
| MinIO API | `http://localhost:9000` |
| MinIO Console | `http://localhost:9001` |
| Keycloak | `http://localhost:8080` |

MinIO Consoleには、`.env`の`MINIO_ROOT_USER`と`MINIO_ROOT_PASSWORD`でログインできます。
Keycloak管理コンソールは`http://localhost:8080/admin`で、初期管理者は`.env`の
`KEYCLOAK_ADMIN_USERNAME`と`KEYCLOAK_ADMIN_PASSWORD`です。これらの値はローカル開発専用です。

### 3. マイグレーションと初期操作者の登録

```bash
mise exec -- just db-migrate

mise exec -- just bootstrap-local-users
```

このコマンドは、realmに固定登録したKeycloakユーザーの`sub`へ、操作者を冪等に紐付けます。

### 4. API、worker、Web UIの起動

3つのターミナルでそれぞれ実行します。

```bash
# Terminal 1: API
mise exec -- just api-dev

# Terminal 2: AI分析・推薦生成・Markdown取り込みworker
mise exec -- uv run --directory apps/api \
  dramatiq app.ai.tasks app.markdown_imports.tasks --processes 1 --threads 4

# Terminal 3: Web UI
mise exec -- just web-dev
```

起動後のURL:

- Web UI: `http://localhost:3000`
- API liveness: `http://localhost:8000/health`
- API readiness: `http://localhost:8000/ready`
- Swagger UI: `http://localhost:8000/docs`

Web UIの「Keycloakでログイン」を選ぶと、認可コード＋PKCEでログインします。
アクセストークンを手入力する必要はありません。
開発サーバーが既存プロセスとの競合で`http://localhost:3001`を使う場合も、ローカルKeycloakは
許可済みです。

| 用途 | ユーザー名 | パスワード | API上の権限 |
|---|---|---|---|
| 管理API・AI設定 | `operator` | `local-dev-password` | `system_operator` |
| 業務データ操作 | `manager` | `local-dev-password` | `manager` |

これらはrealm importで作るローカル開発専用ユーザーです。本番では使用せず、企業IdPの
利用者とOIDC subjectをbootstrapコマンドで登録してください。

### 5. Dockerだけで結合試験を実行する

実IdPや実AI Gatewayを用意せず、Mock OIDC/JWKSとOpenAI互換Gatewayを含む一式を
Docker上で確認する場合は、次を実行します。

```bash
./scripts/run-api-integration-tests.sh
```

このスクリプトは専用のPostgreSQL、Redis、MinIO、API、worker、Mockサービスを起動し、
OIDC認証・部署認可・Markdown取り込み・AI分析・推薦文生成と確定・障害系を検証します。
終了時には専用コンテナとボリュームを自動削除します。

### 6. 停止とデータの初期化

```bash
# コンテナを停止する（データは保持）
docker compose down

# コンテナとローカルDB・MinIOデータを削除する
docker compose down --volumes
```

`--volumes`を付けると登録データと保持中のMarkdown原本が削除されるため、必要な場合だけ
実行してください。

APIの稼働確認は以下で行えます。

```bash
curl http://localhost:8000/health
```

OpenAPI仕様とSwagger UIは、API起動後に以下で確認できます。

- `http://localhost:8000/openapi.json`
- `http://localhost:8000/docs`

## 初期部署・操作者の登録

マイグレーション適用後、OIDCトークンを利用者へ紐付ける前に部署と操作者を登録します。
コマンドは部署コードとメールアドレスをキーに冪等動作し、再実行時は名前、所属部署、
ロール、状態、OIDC subjectを更新します。

```bash
mise exec -- just bootstrap-user \
  --department-code platform \
  --department-name 'プラットフォーム部' \
  --user-name '運用管理者' \
  --email operator@example.com \
  --oidc-subject 'IdPのsubクレーム値' \
  --role system_operator \
  --status active
```

`--role`は`manager`または`system_operator`、`--status`は`active`または`inactive`です。
部署コードは英数字で始まる100文字以内の英数字、`.`、`-`、`_`を使用します。
ロールや所属の変更にも同じコマンドを使えます。OIDC subjectが別の操作者に登録済みの場合は
更新せず失敗し、部署と操作者の変更は単一トランザクションで反映されます。

このコマンドはアクセストークン、クライアントシークレット、パスワードを受け取らず、
OIDC subjectやメールアドレスを標準出力へ表示しません。秘密情報は環境のSecret管理から
アプリケーションへ渡し、コマンドライン引数やリポジトリへ保存しないでください。

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

## CI/CDとリリース

GitHub ActionsはPull Requestと`main`へのpushで、APIのテスト・Ruff・型検査、Webの
テスト・ESLint・型検査・production build、Docker実サービス結合試験、本番APIイメージの
buildを実行します。CodeQLは同じイベントと週次スケジュールで実行します。

リリースはSemantic Versioning形式のタグをpushして作成します。

```bash
git tag -a v1.0.0 -m 'v1.0.0'
git push origin v1.0.0
```

タグのcommitに対してCIがすべて成功すると、Release workflowが以下を配布します。

- GHCR: `ghcr.io/<owner>/<repository>:1.0.0`、`:1.0`、`:1`、`:latest`
- GitHub Release: Linux amd64 Docker image archive（`.docker.tar.zst`）
- CycloneDX JSON SBOM
- `SHA256SUMS`
- GitHub Artifact Attestationによるimageと添付ファイルのprovenance

GHCRから実行する例:

```bash
docker pull ghcr.io/<owner>/<repository>:1.0.0
docker run --rm ghcr.io/<owner>/<repository>:1.0.0 python -m app.bootstrap.cli --help
```

GitHub ReleaseのDocker image archiveを読み込む例:

```bash
sha256sum --check SHA256SUMS
unzstd recommendation-support-api-v1.0.0-linux-amd64.docker.tar.zst
docker load --input recommendation-support-api-v1.0.0-linux-amd64.docker.tar
```

タグを付ける前に、対象commitが`main`へ統合済みで、branch protectionの必須CIが成功している
ことを確認してください。workflowはタグ上でもCIを再実行してから配布します。
