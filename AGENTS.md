# AGENTS.md

このファイルは、このリポジトリでエージェントが Git コミットを作成するときの運用ルールをまとめる。

## コミット前の確認

コミット前に必ず差分とステージ状態を確認する。

```bash
git status
git diff
git diff --cached
```

確認すること:

- 1 コミット 1 目的になっているか
- 不要なファイル、生成物、ログ、秘密情報が含まれていないか
- フォーマット変更と内容変更が混ざっていないか
- 既存のユーザー変更を巻き込んでいないか

## ステージング

意図した変更だけをステージする。

```bash
git add path/to/file
git add -p
```

`git add .` は、対象範囲が明確な場合だけ使う。

## コミット単位

コミット単位は `git/COMMIT_UNIT_GUIDE.md` に従う。

- 1 コミット 1 目的を守る
- レビュー、revert、cherry-pick しやすい単位にする
- `wip` や後追い修正の連続をそのまま残さない
- 必要に応じて `git/cook-book/rebase/` の手順で履歴を整理する

## コミットメッセージ

コミットメッセージは `git/COMMIT_MESSAGE_GUIDE.md` に従い、Conventional Commits 形式にする。

基本形式:

```text
<type>(<scope>): <description>
```

日本語の `description` は体言止めで簡潔に書く。

例:

```text
docs(readme): 開発ガイドラインREADMEの整備
docs(git): rebase手順Cook Bookの追加
fix(config): 設定読み込み失敗時の例外処理
```

## コミット実行

ステージ済み差分を確認してからコミットする。

```bash
git diff --cached
git commit -m "docs(readme): 開発ガイドラインREADMEの整備"
```

コミット後に状態と履歴を確認する。

```bash
git status
git log --oneline --decorate -1
```

## 注意

- 共有済み履歴を書き換える操作は、明示的な依頼がない限り行わない
- `git reset --hard` や `git clean -fd` のような破壊的操作は、明示的な依頼なしに実行しない
- コミット対象外の変更がある場合は、勝手に戻さず対象から外す
