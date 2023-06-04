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
    """Create engine connection to database"""
    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{config.database.user}:{config.database.password}@{config.database.host}/{config.database.dbname}"
    )
    return engine

def create_connection():
    """Create connection to database"""
    conn = psycopg2.connect(
        dbname=config.database.dbname,
        user=config.database.user,
        password=config.database.password,
        host=config.database.host,
    )

    return conn


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
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jl.yd_accounts WHERE is_active is TRUE")
    active_users = [(row[0], row[2], row[5], row[4]) for row in cursor.fetchall()]
    return active_users


def get_users_tg() -> list[tuple[int, str, str, int]]:
    """Get from database users to send Data from Yandex.Direct to telegram bot"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jl.yd_accounts")
    active_users = [(row[1], row[2], row[3], row[5]) for row in cursor.fetchall()]
    return active_users

