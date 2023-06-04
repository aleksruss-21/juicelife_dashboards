import asyncio
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

import datetime


async def direct_run(active_users: list):
    d


def direct_daily(is_test: bool) -> bool:
    from loguru import logger
    from storage.jl_db import get_active_users

    """Parse daily data from Yandex.Direct"""
    logger.info("Launching parse daily data from Direct")
    active_users = get_active_users()
    asyncio.run(direct_run())
    for dashboard_id, token, goal, login in active_users:
        get_report(token=token, dashboard_id=dashboard_id, goals=goal, login=login)
    # logger.info(is_test)
    # users = get_users_tg()
    # for tg_id, login, token, goal in users:
    #     logger.info(tg_id)
    #     mg = get_report_tg(token, goal, login)
    #     if mg is None:
    #         continue
    #     elif mg[0] == "Error":
    #         continue
    #     else:
    #         asyncio.run(telegram_daily(mg, tg_id, login))
    # return True


with DAG(
    dag_id="load-daily-direct",
    schedule="2 6 * * *",
    params = {
        "test_launch": Param(False, type="boolean"),
        "counter_id": Param(type="int"),
        "date_start": Param(type="str"),
        "date_end": Param(type="str")},
    start_date=datetime.datetime(2023, 4, 23),
) as dag:

    t1 = PythonOperator(
        task_id="telegram_daily",
        python_callable=send_report_telegram,
        op_args=["{{params['test_launch']}}"]
        )
    t1
