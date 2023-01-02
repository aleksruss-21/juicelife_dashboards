import asyncio

import pandas
import psycopg2
import sqlalchemy.future

from cfg import config
from loguru import logger

import psycopg
from aiogram.types.message import Message
from sqlalchemy import create_engine


def create_instance() -> sqlalchemy.future.Engine:
    """Create connection to database"""
    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{config.database.user}:{config.database.password}@{config.database.host}/{config.database.dbname}"
    )
    return engine


def upload_direct_from_pandas(df: pandas.DataFrame, dashboard_id: int, connect: sqlalchemy.future.Engine) -> None:
    """Upload report to database using pandas"""
    df.to_sql(f"dashboard_{dashboard_id}", con=connect, if_exists="append", index=False)
    logger.info(f"Successfully uploaded for dashboard_{dashboard_id}!")


def delete_from_report(date: str, dashboard_id: int, conn: sqlalchemy.future.Engine) -> None:
    """Delete from database income dates to upload later"""
    conn.execute(f"DELETE from dashboard_{dashboard_id} WHERE date = '{date}'")


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


def get_users_tg() -> list[tuple[int, int, str, str, int]]:
    """Get from database users to send Data from Yandex.Direct to telegram bot"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dashboards")
    active_users = [(row[0], row[1], row[2], row[4], row[5]) for row in cursor.fetchall()]
    return active_users


async def add_user_tg(message: Message) -> bool:
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
                return True
            else:
                return False


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
