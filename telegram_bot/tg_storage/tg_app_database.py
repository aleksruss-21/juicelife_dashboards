import asyncio
from cfg import config

import psycopg
from aiogram.types.message import Message


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
