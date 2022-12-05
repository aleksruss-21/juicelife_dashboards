from loguru import logger
import os
from dotenv import load_dotenv, find_dotenv

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")
load_dotenv(find_dotenv())


class Config:
    def __init__(self):
        self.database = self.Database()
        self.telegram = self.Telegram()

    class Database:
        def __init__(self):
            self.dbname = "juicelife_dashboards"
            self.user = os.environ.get("LOGIN_DB")
            self.password = os.environ.get("PASSWORD_DB")
            self.host = "postgres12"
            self.async_conn_query = f"dbname={self.dbname} user={self.user} host={self.host} password={self.password}"

    class Telegram:
        def __init__(self):
            self.tg_token = os.environ.get("TG_TOKEN")
            self.tg_nots_token = os.environ.get("TG_NOTS_TOKEN")


def get_instance():
    """Get instance of Config"""
    return Config()
