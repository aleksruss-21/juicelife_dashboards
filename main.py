from service.yandex import get_report
from storage.database import get_active_users
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from service.telegram import run_telegram


def run_daily_upload() -> None:
    """Parse daily data from Yandex.Direct"""
    logger.info("Launching parse daily data from Direct")
    active_users = get_active_users()
    for dashboard_id, token in active_users:
        get_report(token=token, dashboard_id=dashboard_id)


if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone="Europe/Moscow")
    job = scheduler.add_job(run_daily_upload, "cron", hour=15, minute=36)
    scheduler.start()
    run_telegram()
