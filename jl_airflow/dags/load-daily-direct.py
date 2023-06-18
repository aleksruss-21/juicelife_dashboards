import asyncio
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param

import datetime


def direct_daily(account_id: int, date_start: str, date_end: str) -> bool:
    from loguru import logger
    from storage.jl_db import get_active_users
    from service.yandex.yandex_main import load_daily_direct

    """Parse daily data from Yandex.Direct"""
    logger.info("Launching parse daily data from Direct")
    active_users = get_active_users(None if account_id is None else account_id)
    for account_id, login, token, is_agency, goal in active_users:
        load_daily_direct(account_id, login, token, is_agency, goal, date_start, date_end)
    return True


with DAG(
    dag_id="load-daily-direct",
    schedule="2 3 * * *",
    params = {
        "account_id": Param(default=None, type=["null", "integer"]),
        "date_start": Param(default=None, type=["null", "string"]),
        "date_end": Param(default=None, type=["null", "string"])},
    start_date=datetime.datetime(2023, 6, 18),
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id="load-daily-direct",
        python_callable=direct_daily,
        op_args=["{{params['account_id']}}", "{{params['date_start']}}", "{{params['date_end']}}"]
        )
    t1

