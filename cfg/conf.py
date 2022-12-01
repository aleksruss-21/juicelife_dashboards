from loguru import logger

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")


class Config:
    def __init__(self):
        self.database = self.Database()

    class Database:
        def __init__(self):
            self.dbname = "juicelife_dashboards"
            self.user = "admin_juicelife"
            self.password = "mypassword"
            self.host = "postgres12"
            self.async_conn_query = f"dbname={self.dbname} user={self.user} host={self.host} password={self.password}"


def get_instance():
    """Get instance of Config"""
    return Config()
