# ベースイメージ
FROM python:3.13-slim

# 作業ディレクトリの設定
WORKDIR /

# 必要なシステムパッケージのインストール
RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends curl && apt-get clean

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.4

# Poetry のパスを環境変数に追加
ENV PATH="/root/.local/bin:$PATH"

# Poetry の仮想環境をコンテナ外に作成しない設定
RUN poetry config virtualenvs.create false

# プロジェクトの依存パッケージをインストール
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# ソースコードのコピー
COPY . .

# FastAPIアプリケーションの起動（poetry環境内）
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]