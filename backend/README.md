# backend

（サービス名） の API

# 環境構築（Docker）

## 起動 
```bash
$ docker compose up --build
```
→ app / db コンテナが起動し、http://localhost:8000/ にアクセスできることを確認

#### ※ app / db コンテナの入り方
```bash
# app
$ docker exec -it app bash
# db
$ docker exec -it db bash
```

#### ※ 依存パッケージは app コンテナの poetry の仮想環境内にインストールされている
```bash
# app
$ docker exec -it app bash
# db
$ docker exec -it db bash
```

## データベースのマイグレーション

### マイグレーションの追加（不要）
※おそらくセットアップ時にマイグレーションファイルがあるので不要

`/api/models/` にモデルを追加・変更した場合、以下のコマンドでマイグレーションを追加する
```bash
% poetry run alembic revision --autogenerate -m "< メッセージ >"
```
### マイグレーションの適用
※マイグレーションファイル - migration/b1aa4.... の存在を確認してから実行
```bash
% poetry run alembic upgrade head
```

# 環境構築（ローカル）
※Docker環境で動かす場合は不要

| ツール | バージョン |
| --- | --- |
| Python | 3.13.x |
| Poetry | 1.8.x |
| PostgreSQL | 17.x |

## セットアップ

## Python と関連するツールの準備

### Python

```bash
$ python --version
Python 3.13.2
```

### Poetry

※インストール：https://python-poetry.org/  
・ 2.x.x系から仕様変更してるからバージョン指定
```bash
# windows
$ (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -3.13 - --version 1.8.4
```
```bash
# mac
curl -sSL https://install.python-poetry.org | python3 -3.13 - --version1.8.4
```

```bash
$ poetry --version
Poetry (version 1.8.4)
```

### 仮想環境の作成 & 依存パッケージのインストール

```bash
$ poetry install
```
※ poetry shell で仮想環境に入れるが、poetry run ~~~ で仮想環境内のuvicronなどが使える

## データベースの準備

### PostgreSQL

```bash
$ psql --version
psql (PostgreSQL) 17.4
```

### データベースの作成

```bash
$ psql -U postgres
postgres=# CREATE DATABASE trip_planner;
postgres=# CREATE USER trip_planner WITH PASSWORD 'trip_planner';
postgres=# GRANT ALL PRIVILEGES ON DATABASE trip_planner TO trip_planner;
```

## 環境変数

`.env` ファイルを作成し、以下の内容を記述する。
```
ENVIRONMENT='development' 

POSTGRES_USER='trip_planner'
POSTGRES_PASSWORD='trip_planner'
POSTGRES_DB='trip_planner'
POSTGRES_SERVER='localhost'
POSTGRES_PORT='5432'
```

## 起動

```bash
$ poetry run uvicorn app.main:app --reload
```

# データベースのマイグレーション
## マイグレーションの追加

`/api/models/` にモデルを追加・変更した場合、以下のコマンドでマイグレーションを追加する
```
% poetry run alembic revision --autogenerate -m "< メッセージ >"
```

## マイグレーションの適用
```
% poetry run alembic upgrade head
```
