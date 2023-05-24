from loguru import logger
import os
from dotenv import load_dotenv, find_dotenv

logger.add(
    "debug.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="10 MB",
    compression="zip",
)
load_dotenv(find_dotenv())


class Config:
    def __init__(self):
        self.database = self.Database()
        self.telegram = self.Telegram()
        self.yandex = self.Yandex()

    class Database:
        def __init__(self):
            self.dbname = os.environ.get("POSTGRES_DB")
            self.user = os.environ.get("POSTGRES_USER")
            self.password = os.environ.get("POSTGRES_PASSWORD")
            # self.host = "postgres"
            self.host = "194.67.111.233"
            self.async_conn_query = f"dbname={self.dbname} user={self.user} host={self.host} password={self.password}"

    class Telegram:
        def __init__(self):
            self.tg_token = os.environ.get("TG_TOKEN")
            self.tg_nots_token = os.environ.get("TG_NOTS_TOKEN")

    class Yandex:
        def __init__(self):
            self.yandex_client_id = os.environ.get("YANDEX_CLIENT_ID")
            self.yandex_client_secret = os.environ.get("YANDEX_CLIENT_SECRET")


def get_instance():
    """Get instance of Config"""
    return Config()
