from service.yandex import get_report, get_report_tg
from storage.database import get_active_users, get_users_tg
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from service.telegram import run_telegram, telegram_daily
import asyncio


def run_daily_upload() -> None:
    """Parse daily data from Yandex.Direct"""
    logger.info("Launching parse daily data from Direct")
    active_users = get_active_users()
    for dashboard_id, token, goal in active_users:
        get_report(token=token, dashboard_id=dashboard_id, goals=goal)


def send_report_telegram() -> None:
    """Send report to telegram bot"""
    logger.info("Preparing to send report to telegram")
    users = get_users_tg()
    for dashboard_id, tg_id, token, login, goal in users:
        mg = get_report_tg(token, dashboard_id, goal, tg_id, login)
        asyncio.run(telegram_daily(mg, tg_id))

run_telegram()

# if __name__ == "__main__":
#     scheduler = BackgroundScheduler(timezone="Europe/Moscow")
#     job = scheduler.add_job(run_daily_upload, "cron", hour=2, minute=10)
#     tg_daily_job = scheduler.add_job(send_report_telegram, "cron", hour=9, minute=2)
#     scheduler.start()
#     run_telegram()
