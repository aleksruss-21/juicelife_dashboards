from service.yandex_queries import get_daily_data_request
from service.process import process_direct
from loguru import logger
import time


def get_report(token: str, dashboard_id: int) -> None:
    """Request data from Direct"""
    response_report = get_daily_data_request(token, dashboard_id)
    if response_report.status_code == 200:
        logger.info("Successfully connected to Direct")
        csv_direct = response_report.text
        process_direct(csv_direct, dashboard_id)
    elif response_report.status_code == 201:
        time.sleep(20)
        get_report(token, dashboard_id)
    else:
        logger.error(
            f"Error while connecting to Yandex.Direct. Response {response_report.status_code}. {response_report.text}"
        )
