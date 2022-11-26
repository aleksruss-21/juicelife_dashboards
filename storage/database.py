import psycopg2
from cfg import config
from loguru import logger


def upload_direct(report: str, dashboard_id: int) -> None:
    """Upload report from Yandex.Direct to database"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute(
        f"""
CREATE TABLE IF NOT EXISTS dashboard_{dashboard_id} (
    date DATE NOT NULL,
    campaign_id INTEGER NOT NULL,
    campaign_name VARCHAR,
    criterion VARCHAR,
    impressions INTEGER,
    clicks INTEGER,
    cost REAL,
    conversions INTEGER
);

INSERT INTO dashboard_{dashboard_id} (date, campaign_id, campaign_name, criterion, impressions, clicks, cost)
VALUES ({report}) """
    )
    conn.commit()
    conn.close()
    logger.info(f"Successfully uploaded to database from Yandex.Direct. {report}")


def get_active_users() -> list[tuple[int, str]]:
    """Get from database active users for getting Data from Yandex.Direct"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dashboards WHERE active = '1'")
    active_users = [(row[0], row[2]) for row in cursor.fetchall()]
    return active_users
