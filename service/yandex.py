import service.yandex_queries
from service.yandex_queries import get_daily_data_request, get_daily_data_request_tg
from service.process import process_direct, process_direct_tg, make_messages
from loguru import logger
import time
from datetime import datetime, timedelta


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
    if campaign == "No campaigns":
        return "No campaigns"
    response_report = await service.yandex_queries.get_arr_goals(token, campaign)
    if response_report.status_code == 200:
        goals = [{"name": item["Name"], "goal_id": item["GoalID"]} for item in response_report.json()["data"]]
        return goals
    else:
        logger.error(f"Error while getting goals. {response_report.status_code}, {response_report.text}")


async def get_arr_campaigns(token: str) -> str | None:
    """Process yandex query to get campaign ID"""
    resp = await service.yandex_queries.get_arr_campaigns(token)

    if resp.status_code == 200:
        arr = resp.text.split("\n")[1]
        if arr == "":
            return "No campaigns"
        return arr
    else:
        logger.error(f"Error while getting list of campaigns to get login. {resp.status_code}, {resp.text}")
        return None


def get_report_tg(token: str, goals: int, login: str) -> tuple[str, str, str] | list[str]:
    """Request data from Direct"""
    response_report = get_daily_data_request_tg(token, goals)
    if response_report.status_code == 200:
        logger.info(f"Successfully connected to Direct {login}")
        csv_direct = response_report.text
        df = process_direct_tg(csv_direct)
        if df is None:
            yesterday = datetime.strftime(datetime.now() - timedelta(days=1), "%d.%m.%Y")
            return [f"<b>📅 {login} | Не было рекламных кампаний за {yesterday}\n\n</b>"]
        tg_message = make_messages(df, login)
        return tg_message
    else:
        logger.error(
            f"Error while connecting to Yandex.Direct {login}. Response {response_report.status_code}. "
            f"{response_report.text}"
        )
