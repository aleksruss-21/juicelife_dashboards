import asyncio

import service.yandex_queries
from service.yandex_queries import get_daily_data_request, get_daily_data_request_tg
from service.process import process_direct, process_direct_tg, make_messages
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


async def arr_goals(token: str) -> list[dict] | str:
    """Process yandex query to get goals"""
    campaign = await get_arr_campaigns(token)
    response_report = await service.yandex_queries.get_arr_goals(token, campaign)
    if response_report.json().get("data") is None:
        logger.debug("Key Error. 'data'")
        return "Error | Key Error"
    if response_report.status_code == 200:
        goals = [{"name": item["Name"], "goal_id": item["GoalID"]} for item in response_report.json()["data"]]
        return goals
    else:
        logger.error(f"Error while getting goals. {response_report.status_code}, {response_report.text}")


async def get_arr_campaigns(token: str) -> str:
    """Process yandex query to get campaign ID"""
    resp = await service.yandex_queries.get_arr_campaigns(token)

    if resp.status_code == 200:
        try:
            arr = resp.text.split("\n")[1]
            return arr
        except IndexError:
            logger.error("IndexError")
    elif resp.status_code == 201 or resp.status_code == 202:
        await asyncio.sleep(1)
        await get_arr_campaigns(token)
    else:
        logger.error(f"Error while getting list of campaigns to get login. {resp.status_code}, {resp.text}")
        await get_arr_campaigns(token)


def get_report_tg(token: str, dashboard_id: int, goals: int, tg_id: int, login: str) -> tuple[str, str, str]:
    """Request data from Direct"""
    response_report = get_daily_data_request_tg(token, dashboard_id, goals)
    if response_report.status_code == 200:
        logger.info(f"Successfully connected to Direct {login}")
        csv_direct = response_report.text
        df = process_direct_tg(csv_direct)
        tg_message = make_messages(df, login)
        return tg_message

    elif response_report.status_code == 201 or response_report.status_code == 202:
        time.sleep(20)
        get_report_tg(token, dashboard_id, goals, tg_id, login)
    else:
        logger.error(
            f"Error while connecting to Yandex.Direct {login}. Response {response_report.status_code}. "
            f"{response_report.text}"
        )
