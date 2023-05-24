import asyncio
from airflow import DAG
from airflow.operators.python import PythonOperator

import datetime


def send_report_telegram() -> bool:
    from loguru import logger
    from telegram_bot.tg_storage.tg_app_database import get_users_tg
    from telegram_bot.tg_service.tg_menu_main import get_report_tg, telegram_daily

    """Send report to telegram bot"""
    logger.info("Preparing to send report to telegram")
    users = get_users_tg()
    for tg_id, login, token, is_agency, goal in users:
        mg = get_report_tg(token, goal, login, is_agency)
        if mg is None:
            continue
        elif mg[0] == "Error":
            continue
        else:
            asyncio.run(telegram_daily(mg, tg_id, login))
    return True


with DAG(
    dag_id="send-daily-telegram",
    schedule="2 6 * * *",
    start_date=datetime.datetime(2023, 4, 23),
) as dag:

    t1 = PythonOperator(task_id="telegram_daily", python_callable=send_report_telegram)
    t1
    # t1 = BashOperator(
    #     task_id='echo_hi',
    #     bash_command='echo "Hello"',
    # )
    # t2 = BashOperator(
    #     task_id='print_date',
    #     bash_command='date',
    # )
    # t1 >> t2
