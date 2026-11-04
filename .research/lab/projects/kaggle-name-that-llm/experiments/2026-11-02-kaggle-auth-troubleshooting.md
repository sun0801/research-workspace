---
date: 2026-11-02
project: kaggle-name-that-llm
type: environment-diagnosis
---

# Kaggle認証トラブルと対応

## 確認した事実

ユーザー端末ではcodexがPATH上になく、VS Code拡張同梱の実行ファイルを案内した。移設先のプロジェクト設定もCLIに読み込まれていなかったため、ユーザー設定へ既存の読み取り32ツールの設定を追加し、認識を確認した。

その後、本人が開いた認証画面で `Invalid auth scope: resources.admin:` が発生。KaggleのOAuthメタデータは `resources.admin:*` を宣言している。個人の資格情報を使わない診断リクエストで、末尾のアスタリスクを省くと同じ400エラーになることを確認した。どの段階で文字が欠けたかは確定していない。

正しいスコープをリテラル/URLエンコードの両方で送ると、別の400エラー `ClientId too small: codex` を返した。CodexのDCR指定でも発行URLのclient_idはcodexのままだった。サーバ全般のOAuth障害とは断定せず、この経路でのログイン完了を見込めないため方式を変更する。

## 対応

Kaggle公式MCPドキュメントに記載されたAPIトークン方式を用意した。本人がSettingsで発行したトークンを `scripts/configure_token.py` の非表示入力で保存する。権限600の.envを既存設定を保持して更新し、認証が必要なNotebook検索で検証する。MCPのhttp_headers_helperと収集ツールは同じ保存先を参照する。秘密値はCodex設定や研究記録へ書かない。

保存時の権限・他設定の保持・ヘルパーの形式・無効入力時の非保存を追加テストし、既存テストと合わせて7件通過。Codexがhttp_headers_helper設定を受け付けることを確認。

## 未完了（診断時点）

本人のトークン設定、有効トークンでの実接続、Notebook精読。認証や学習が完了したとは扱わない。トークン保存後、既存のネイティブMCP接続は再接続が必要な場合がある。

## 出典

- [Kaggle MCPの認証説明](https://www.kaggle.com/docs/mcp)
- [OAuthメタデータ](https://www.kaggle.com/.well-known/oauth-authorization-server)
- [公式CLI認証リファレンス](https://github.com/Kaggle/kaggle-cli/blob/main/skills/references/auth.md)
- [Codex設定スキーマ](https://developers.openai.com/codex/config-schema.json)

## 追記 16:55 — トークン認証成功

ユーザーがトークン設定とNotebook検索成功を報告。こちらでもローカルMCPクライアントの収集9項目と、公式CLIによる公開Notebook 3本のコード取得に成功した。トークン設定とローカル接続の確認は完了。既存のネイティブMCP接続はUnauthenticatedだったため、そちらの再接続確認は残る。詳細は[取得確認](2026-11-02-authenticated-notebook-discovery.md)。
