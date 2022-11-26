import psycopg2
from cfg import config
from loguru import logger


def upload_direct(report: str) -> None:
    """Upload report from Yandex.Direct to database"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute(
        f"""INSERT INTO coral_travel_direct (date, campaign_id, campaign_name, impressions, clicks, cost,
conversion_flight_choose, conversion_input_data, conversion_booked) VALUES ({report})"""
    )
    conn.commit()
    conn.close()
    logger.info(f"Successfully uploaded to database from Yandex.Direct. {report}")


def upload_metrika(report: str) -> None:
    """Upload report from Yandex.Metrika to database"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO coral_travel_metrika (date, campaign_id, campaign_name, transactions, revenue) VALUES ({report})"
    )
    conn.commit()
    conn.close()
    logger.info(f"Successfully uploaded to database from Yandex.Metrika. {report}")

