import service.yandex_queries
from service.yandex_queries import get_daily_data_request
from service.process import process_direct
from loguru import logger
import time


def get_report(token: str, dashboard_id: int, goals: int) -> None:
    """Request data from Direct"""
    response_report = get_daily_data_request(token, dashboard_id, goals)
    if response_report.status_code == 200:
        logger.info("Successfully connected to Direct")
        csv_direct = response_report.text
        process_direct(csv_direct, dashboard_id)
    elif response_report.status_code == 201 or response_report.status_code == 202:
        time.sleep(20)
        get_report(token, dashboard_id, goals)
    else:
        logger.error(
            f"Error while connecting to Yandex.Direct. Response {response_report.status_code}. {response_report.text}"
        )


async def arr_goals(token: str) -> list[dict]:
    """Process yandex query to get goals"""
    campaign = await get_arr_campaigns(token)
    response_report = await service.yandex_queries.get_arr_goals(token, campaign)
    goals = [{"name": item["Name"], "goal_id": item["GoalID"]} for item in response_report.json()["data"]]
    return goals


async def get_arr_campaigns(token: str) -> str:
    """Process yandex query to get campaign ID"""
    resp = await service.yandex_queries.get_arr_campaigns(token)
    try:
        arr = resp.text.split("\n")[1]
        return arr
    except IndexError:
        await get_arr_campaigns(token)
