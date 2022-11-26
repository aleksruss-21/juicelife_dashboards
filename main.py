from service.yandex import get_report
from service.metrika import get_metrika
from apscheduler.schedulers.background import BlockingScheduler
from loguru import logger


def run() -> None:
    """Parse data from Yandex.Direct and Yandex.Metrika"""
    logger.info("Launching parse from Direct and Metrika.")
    get_report()
    get_metrika()

run()


# if __name__ == "__main__":
#     scheduler = BlockingScheduler(timezone="Europe/Moscow")
#     job = scheduler.add_job(run, "cron", hour=4, minute=12)
#     scheduler.start()

