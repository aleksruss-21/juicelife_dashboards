import asyncio

import psycopg2
from cfg import config
from loguru import logger

import psycopg
from aiogram.types.message import Message


def upload_direct(report: str, dashboard_id: int) -> None:
    """Upload report from Yandex.Direct to database"""
    arr_report = report.split('|||')
    date_row = arr_report[0]
    campaign_id = arr_report[1]
    ad_group_id = arr_report[4]
    age = arr_report[6]
    target_location_id = arr_report[7]
    gender = arr_report[9]
    criterion = arr_report[11]
    device = arr_report[13]

    impressions = arr_report[14]
    clicks = arr_report[15]
    cost = arr_report[16]
    bounces = arr_report[17]
    conversions = arr_report[18]

    report = report.replace("|||", ",")

    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute(
        f"""
    SELECT EXISTS (SELECT * FROM dashboard_{dashboard_id} WHERE
        date = {date_row} AND
        campaign_id = {campaign_id} AND
        ad_group_id = {ad_group_id} AND
        age = {age} AND
        targeting_location_id = {target_location_id} AND
        gender = {gender} AND
        criterion_id = {criterion} AND
        device = {device});""")
    if cursor.fetchone()[0] is True:
        cursor.execute(f"""
        UPDATE dashboard_{dashboard_id}
             SET
                impressions = {impressions},
                clicks = {clicks},
                cost = {cost},
                bounces = {bounces},
                conversions = {conversions}
             WHERE
                date = {date_row} AND
                campaign_id = {campaign_id} AND
                ad_group_id = {ad_group_id} AND
                age = {age} AND
                targeting_location_id = {target_location_id} AND
                gender = {gender} AND
                criterion_id = {criterion} AND
                device = {device};"""
                       )
    else:
        cursor.execute(f"""INSERT INTO dashboard_{dashboard_id} VALUES ({report})""")
    conn.commit()
    conn.close()
    logger.info(f"Successfully uploaded to database from Yandex.Direct. {report}")


def get_active_users() -> list[tuple[int, str, int]]:
    """Get from database active users for getting Data from Yandex.Direct"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dashboards WHERE active = '1'")
    active_users = [(row[0], row[2], row[5]) for row in cursor.fetchall()]
    return active_users


async def add_user_tg(message: Message) -> None:
    """Add to database new user of Telegram Bot"""

    query = (
        f"INSERT INTO tg_users (telegram_id, first_name, last_name, username) VALUES "
        f"('{message.chat.id}', '{message.chat.first_name}', '{message.chat.last_name}', '{message.chat.username}')"
    )

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM tg_users WHERE telegram_id = {message.chat.id}")
            if await cur.fetchone() is None:
                await cur.execute(query)


async def add_token_direct(telegram_id: int, token: str, login_direct: str) -> None:
    """Add to database new ad account"""
    lock = asyncio.Lock()

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM dashboards WHERE user_id = {telegram_id} AND login = '{login_direct}'")
            if await cur.fetchone() is None:
                async with lock:
                    await cur.execute("SELECT COUNT(dashboard_id) FROM dashboards")
                    count_dashboards = await cur.fetchone()
                query = (
                    f"INSERT INTO dashboards (dashboard_id, user_id, token, active, login) "
                    f"VALUES ('{count_dashboards[0] + 1}', '{telegram_id}', 'Bearer {token}', '0', '{login_direct}')"
                )
                await cur.execute(query)
            else:
                await cur.execute(
                    f"UPDATE dashboards SET token = '{token}' WHERE user_id = {telegram_id}"
                    f" AND login = '{login_direct}'"
                )


async def add_goal_id_direct(telegram_id: int, goal_id: str, login_direct: str) -> None:
    """Add to database new ad account"""

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE dashboards SET goals_1 = '{goal_id}' WHERE user_id = {telegram_id}"
                f" AND login = '{login_direct}'"
            )


async def get_users_accounts(message: Message) -> list:
    """Get user's accounts from Direct"""

    query = f"SELECT login FROM dashboards WHERE user_id = {message.chat.id}"

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
            accounts = await cur.fetchall()
            return accounts


async def delete_dashboard_token(telegram_id: int, login: str) -> None:
    """Delete user's accounts from Direct"""

    query = (
        f"UPDATE dashboards SET user_id = NULL, token = NULL, active = '0' WHERE user_id = {telegram_id}"
        f" AND login = '{login}'"
    )

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
