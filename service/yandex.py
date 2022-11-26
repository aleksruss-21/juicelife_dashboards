import requests
from service.process import process_direct
from cfg import config
from loguru import logger
import time


def get_report():
    """Request data from Direct"""
    response_report = requests.get(
        config.yandex_direct.url_direct_report,
        json=config.yandex_direct.direct_params_report,
        headers=config.yandex_direct.direct_headers,
    )
    if response_report.status_code == 200:
        logger.info("Successfully connected to Direct")
        csv_direct = response_report.text.replace("\t", ",")
        process_direct(csv_direct)
    elif response_report.status_code == 201:
        time.sleep(20)
        get_report()
    else:
        logger.error(
            f"Error while connecting to Yandex.Direct. Response {response_report.status_code}. {response_report.text}"
        )
