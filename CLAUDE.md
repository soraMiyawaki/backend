# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

OpenAI連携を持つFastAPIバックエンドサービス。チャット補完APIを提供し、標準レスポンスとストリーミングレスポンスの両方に対応。

## アーキテクチャ

- **エントリーポイント**: `app/main.py` - CORSミドルウェア付きFastAPIアプリケーション
- **設定**: `app/config.py` - .envサポート付きPydantic設定
- **ルーター**: `app/routers/chat.py` - チャットエンドポイント (`/api/chat`, `/api/chat/stream`)
- **サービス**: `app/services/openai_service.py` - httpxを使ったOpenAI APIクライアント
- **スキーマ**: `app/schemas.py` - リクエスト/レスポンス検証用Pydanticモデル

### 主要な設計パターン

- 環境変数は起動時に`python-dotenv`で読み込み（親ディレクトリからの実行にも対応）
- 設定はPydantic Settingsを使用し、型安全な環境変数アクセスを実現
- OpenAI API呼び出しには非同期httpxクライアントを使用（タイムアウトなし）
- SSEストリーミング実装は`data:`行をパースし、deltaコンテンツチャンクをyield

## 開発コマンド

### セットアップ
```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境設定
# .envファイルを作成: OPENAI_API_KEY, MODEL (デフォルト: gpt-4o-mini), OPENAI_API_BASE (デフォルト: https://api.openai.com/v1)
```

### 実行
```bash
# 開発サーバーの起動
uvicorn app.main:app --reload

# ホスト/ポート指定で起動
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 環境変数

`.env`ファイルに設定が必要:
- `OPENAI_API_KEY` - OpenAI APIキー（LLM機能に必須）
- `FRONTEND_ORIGIN` - CORS許可オリジン（デフォルト: http://localhost:5173）
- `MODEL` - モデル名（デフォルト: gpt-4o-mini）
- `OPENAI_API_BASE` - APIベースURL（デフォルト: https://api.openai.com/v1）
- `PROVIDER` - LLMプロバイダー、"openai"または"echo"（デフォルト: echo）
- `DEBUG` - デバッグモード（デフォルト: True）

## APIエンドポイント

### POST /api/chat
非ストリーミングのチャット補完。単一のレスポンスを返す。

リクエスト: `{ messages: [{role, content}], temperature?, max_tokens? }`
レスポンス: `{ content: string }`

### POST /api/chat/stream
SSE経由のストリーミングチャット補完。

リクエスト: `/api/chat`と同じ
レスポンス: コンテンツチャンクの`text/plain`ストリーム
