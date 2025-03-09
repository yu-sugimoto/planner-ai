# DB接続テスト用のスクリプト（単体実行ファイル）
# $ poetry run python -m app.test_connection
# 接続成功 → データベースへの接続が成功しました

from sqlalchemy import text
from app.database import engine
from sqlalchemy.exc import OperationalError

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 'データベースへの接続が成功しました'"))
        print(result.scalar())
except OperationalError as e:
    print(f"データベースエラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")