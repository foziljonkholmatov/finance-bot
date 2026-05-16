"""
core/database.py — Async PostgreSQL pool (psycopg3)
"""
from __future__ import annotations
from typing import Optional

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from core.config import DB_DSN

pool: AsyncConnectionPool | None = None


async def init_pool() -> None:
    global pool
    pool = AsyncConnectionPool(
        conninfo=DB_DSN, min_size=2, max_size=10,
        open=False, kwargs={"row_factory": dict_row},
    )
    await pool.open()
    await pool.wait()


async def close_pool() -> None:
    if pool:
        await pool.close()


def get_pool() -> AsyncConnectionPool:
    if pool is None:
        raise RuntimeError("Pool ishga tushurilmagan. init_pool() ni chaqiring.")
    return pool
