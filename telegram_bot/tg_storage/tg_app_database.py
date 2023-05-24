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


def check_exists_dash(dashboard_id: int, cur: sqlalchemy.future.Engine) -> bool:
    """Check if exists table"""
    query = (
        f"SELECT EXISTS (SELECT FROM pg_tables WHERE pg_tables.schemaname = 'public' "
        f"AND tablename = 'dashboard_{dashboard_id}')"
    )
    result = cur.execute(query).fetchone()[0]
    return result


def get_active_users() -> list[tuple[int, str, int, str]]:
    """Get from database active users for getting Data from Yandex.Direct"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jl.yd_accounts WHERE is_active = '1'")
    active_users = [(row[0], row[2], row[5], row[4]) for row in cursor.fetchall()]
    return active_users


def get_users_tg() -> list[tuple[int, str, str, bool, int]]:
    """Get from database users to send Data from Yandex.Direct to telegram bot"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jl.yd_accounts")
    active_users = [(row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()]
    return active_users


async def add_user_tg(message: Message) -> bool:
    """Add to database new user of Telegram Bot"""

    query = (
        f"INSERT INTO jl.tg_users (telegram_id, first_name, last_name, username) VALUES "
        f"('{message.chat.id}', '{message.chat.first_name}', '{message.chat.last_name}', '{message.chat.username}')"
    )

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM jl.tg_users WHERE telegram_id = {message.chat.id}")
            if await cur.fetchone() is None:
                await cur.execute(query)
                return True
            else:
                return False


async def add_token_direct(telegram_id: int, token: str, login_direct: str, agency: bool = False) -> None:
    """Add to database new ad account"""
    lock = asyncio.Lock()

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM jl.yd_accounts WHERE telegram_id = {telegram_id} AND login = '{login_direct}'"
            )
            if await cur.fetchone() is None:
                async with lock:
                    await cur.execute("SELECT COUNT(account_id) FROM jl.yd_accounts")
                    count_dashboards = await cur.fetchone()
                query = (
                    f"INSERT INTO jl.yd_accounts "
                    f"VALUES ('{count_dashboards[0] + 1}', '{telegram_id}', '{login_direct}', '{token}', '{agency}')"
                )
                await cur.execute(query)
            else:
                await cur.execute(
                    f"UPDATE jl.yd_accounts SET token = '{token}' WHERE telegram_id = {telegram_id}"
                    f" AND login = '{login_direct}'"
                )


async def add_goal_id_direct(telegram_id: int, goal_id: str, login_direct: str) -> None:
    """Add to database new ad account"""

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE jl.yd_accounts SET goal_id = '{goal_id}' WHERE telegram_id = {telegram_id}"
                f" AND login = '{login_direct}'"
            )


async def get_users_accounts(message: Message) -> list:
    """Get user's accounts from Direct"""

    query = f"SELECT login FROM jl.yd_accounts WHERE telegram_id = {message.chat.id} AND token IS NOT NULL"

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
            accounts = await cur.fetchall()
            return accounts


async def delete_dashboard_token(telegram_id: int, login: str) -> None:
    """Delete user's accounts from Direct"""
    query = f"UPDATE jl.yd_accounts SET token = NULL WHERE telegram_id = {telegram_id}" f" AND login = '{login}'"

    async with await psycopg.AsyncConnection.connect(config.database.async_conn_query) as conn:
        async with conn.cursor() as cur:
            await cur.execute(query)
