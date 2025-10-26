import os
from urllib.parse import urlparse

from .Singleton import SingletonDatabase

def connect_DB(connect_str="CONNECTION_STRING"):
    conn_url = os.getenv(connect_str)
    if not conn_url:
        raise RuntimeError(
            f"환경 변수 '{connect_str}'를 찾을 수 없습니다. .env 설정을 확인하세요."
        )

    if isinstance(conn_url, bytes):
        conn_url = conn_url.decode()

    url = urlparse(conn_url)
    path = url.path
    if isinstance(path, bytes):
        path = path.decode()

    config = {
        "host": url.hostname,
        "port": url.port,
        "user": url.username,
        "password": url.password,
        "dbname": path.lstrip("/"),
    }
    return SingletonDatabase(config)
