# ADR-011: AI機能を専門コンポーネントへ分割する

## 状態

採用

## 決定

Markdown Parser、Project Analyzer、Evidence Finder、Recommendation Generator、Warning Generatorへ責務を分割し、AI Orchestratorが統括する。

## 理由

プロンプト、モデル、検証、障害対応を用途別に管理しやすくするため。
