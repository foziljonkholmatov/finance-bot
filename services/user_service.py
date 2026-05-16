"""
services/user_service.py — Foydalanuvchi bilan bog'liq barcha DB operatsiyalar
"""
from __future__ import annotations
from typing import Optional
from core.database import get_pool


async def upsert_user(user_id: int, username: str | None, full_name: str) -> None:
    async with get_pool().connection() as conn:
        await conn.execute(
            """
            INSERT INTO users (id, username, full_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE
                SET username = EXCLUDED.username,
                    full_name = EXCLUDED.full_name
            """,
            (user_id, username, full_name),
        )


async def get_user(user_id: int) -> Optional[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return await r.fetchone()


async def complete_registration(
    user_id: int, phone: str, latitude: float, longitude: float
) -> None:
    async with get_pool().connection() as conn:
        await conn.execute(
            """
            UPDATE users
            SET phone=%s, latitude=%s, longitude=%s, is_registered=TRUE
            WHERE id=%s
            """,
            (phone, latitude, longitude, user_id),
        )


async def set_admin(user_id: int, is_admin: bool = True) -> None:
    async with get_pool().connection() as conn:
        await conn.execute(
            "UPDATE users SET is_admin=%s WHERE id=%s", (is_admin, user_id)
        )


async def set_blocked(user_id: int, blocked: bool) -> None:
    async with get_pool().connection() as conn:
        await conn.execute(
            "UPDATE users SET is_blocked=%s WHERE id=%s", (blocked, user_id)
        )


async def get_all_users(limit: int = 50, offset: int = 0) -> list[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT id, username, full_name, phone,
                   is_registered, is_blocked, is_admin, created_at
            FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        return await r.fetchall()


async def get_users_count() -> dict:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE is_registered) AS registered,
                   COUNT(*) FILTER (WHERE is_blocked)    AS blocked
            FROM users
            """
        )
        return await r.fetchone()


async def is_admin(user_id: int) -> bool:
    user = await get_user(user_id)
    return bool(user and user.get("is_admin"))


async def is_registered(user_id: int) -> bool:
    user = await get_user(user_id)
    return bool(user and user.get("is_registered"))
