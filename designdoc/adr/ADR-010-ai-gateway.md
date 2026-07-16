# ADR-010: AI GatewayとOpenAI互換Custom Providerを採用する

## 状態

採用

## 決定

アプリケーションはAI GatewayへOpenAI互換APIで接続する。  
接続はCustom Providerとして扱う。

## 理由

モデルや提供元の切り替えを容易にし、アプリケーションを特定ベンダーへ密結合させない。
