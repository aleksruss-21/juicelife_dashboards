from service.yandex import get_report
from storage.database import get_active_users
from apscheduler.schedulers.background import BlockingScheduler
from loguru import logger


def run_daily_upload() -> None:
    """Parse daily data from Yandex.Direct"""
    logger.info("Launching parse daily data from Direct")
    active_users = get_active_users()
    for dashboard_id, token in active_users:
        get_report(token=token, dashboard_id=dashboard_id)


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Europe/Moscow")
    job = scheduler.add_job(run_daily_upload, "cron", hour=4, minute=12)
    scheduler.start()
