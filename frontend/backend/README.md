# backend

（仮）trip_planner の API

## 目次

-   [環境構築（Docker）](#環境構築docker)
-   [環境構築（Dockerでうまくいかない場合）](#環境構築dockerでうまくいかない場合)
-   [データベースのマイグレーション](#データベースのマイグレーション)
-   [初期データ投入](#初期データの投入)

## 環境構築（Docker）

## 起動 
```
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
# app コンテナ
$ docker exec -it app bash
$ poetry show
```

<br>

***

<br>

## 環境構築（Dockerでうまくいかない場合）
※Docker環境で動かす場合は不要

| ツール | バージョン |
| --- | --- |
| Python | 3.13.x |
| Poetry | 1.8.x |
| PostgreSQL | 17.x |

## セットアップ

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
$ curl -sSL https://install.python-poetry.org | python3 -3.13 - --version1.8.4
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
```
$ psql -U postgres
postgres=# CREATE DATABASE trip_planner;
postgres=# CREATE USER trip_planner WITH PASSWORD 'trip_planner';
postgres=# GRANT ALL PRIVILEGES ON DATABASE trip_planner TO trip_planner;
```

## 環境変数の編集
`.env` ファイルを作成し、以下の内容を記述する。
```bash
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

<br>

***

<br>

## データベースのマイグレーション

### マイグレーションの追加（不要）
※おそらくセットアップ時にマイグレーションファイルがあるので不要  
`/api/models/` にモデルを追加・変更した場合、以下のコマンドでマイグレーションを追加する
```
$ poetry run alembic revision --autogenerate -m "< メッセージ >"
```

### マイグレーションの適用
```bush
$ poetry run alembic upgrade head
```

<br>

***

<br>

## 初期データの投入

### 施設・観光地データをDBに保存
```bush
$ poetry run python -m app.add_spots
```