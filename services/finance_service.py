"""
services/finance_service.py — Tranzaksiya, kategoriya, hisobot operatsiyalar
"""
from __future__ import annotations
from typing import Optional
from core.database import get_pool


# ── Kategoriyalar ─────────────────────────────────────────────────────────────

async def get_categories(type_: str) -> list[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            "SELECT id, name FROM categories WHERE type=%s ORDER BY id", (type_,)
        )
        return await r.fetchall()


# ── Tranzaksiyalar ────────────────────────────────────────────────────────────

async def add_transaction(
    user_id: int, type_: str, amount: int,
    currency: str, amount_original: float,
    category_id: int, note: str = "",
) -> dict:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            INSERT INTO transactions
              (user_id, type, amount, currency, amount_original, category_id, note)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id, amount, created_at
            """,
            (user_id, type_, amount, currency, amount_original, category_id, note),
        )
        return await r.fetchone()


async def get_user_transactions(
    user_id: int, limit: int = 10, offset: int = 0
) -> list[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT t.id, t.type, t.amount, t.currency, t.amount_original,
                   t.note, c.name AS category, t.created_at
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.user_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (user_id, limit, offset),
        )
        return await r.fetchall()


async def get_transaction(tx_id: int, user_id: int) -> Optional[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT t.*, c.name AS category
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.id=%s AND t.user_id=%s
            """,
            (tx_id, user_id),
        )
        return await r.fetchone()


async def update_transaction_amount(
    tx_id: int, user_id: int,
    amount: int, amount_original: float, currency: str
) -> bool:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            UPDATE transactions
            SET amount=%s, amount_original=%s, currency=%s, updated_at=NOW()
            WHERE id=%s AND user_id=%s RETURNING id
            """,
            (amount, amount_original, currency, tx_id, user_id),
        )
        return await r.fetchone() is not None


async def update_transaction_note(tx_id: int, user_id: int, note: str) -> bool:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            "UPDATE transactions SET note=%s, updated_at=NOW() WHERE id=%s AND user_id=%s RETURNING id",
            (note, tx_id, user_id),
        )
        return await r.fetchone() is not None


async def delete_transaction(tx_id: int, user_id: int) -> bool:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            "DELETE FROM transactions WHERE id=%s AND user_id=%s RETURNING id",
            (tx_id, user_id),
        )
        return await r.fetchone() is not None


async def delete_last_transaction(user_id: int) -> Optional[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            DELETE FROM transactions WHERE id=(
                SELECT id FROM transactions WHERE user_id=%s
                ORDER BY created_at DESC LIMIT 1
            ) RETURNING id, type, amount
            """,
            (user_id,),
        )
        return await r.fetchone()


# ── Hisobotlar ────────────────────────────────────────────────────────────────

async def get_today_summary(user_id: int) -> dict:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT
                COALESCE(SUM(amount) FILTER (WHERE type='income'),  0) AS income,
                COALESCE(SUM(amount) FILTER (WHERE type='expense'), 0) AS expense,
                COUNT(*) AS count
            FROM transactions
            WHERE user_id=%s AND created_at::date = CURRENT_DATE
            """,
            (user_id,),
        )
        return await r.fetchone()


async def get_monthly_summary(user_id: int, year: int, month: int) -> dict:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT
                COALESCE(SUM(amount) FILTER (WHERE type='income'),  0) AS income,
                COALESCE(SUM(amount) FILTER (WHERE type='expense'), 0) AS expense,
                COUNT(*) AS count
            FROM transactions
            WHERE user_id=%s
              AND EXTRACT(YEAR  FROM created_at)=%s
              AND EXTRACT(MONTH FROM created_at)=%s
            """,
            (user_id, year, month),
        )
        return await r.fetchone()


async def get_category_breakdown(
    user_id: int, type_: str, year: int, month: int
) -> list[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT c.name AS category, SUM(t.amount) AS total, COUNT(*) AS cnt
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.user_id=%s AND t.type=%s
              AND EXTRACT(YEAR  FROM t.created_at)=%s
              AND EXTRACT(MONTH FROM t.created_at)=%s
            GROUP BY c.name ORDER BY total DESC
            """,
            (user_id, type_, year, month),
        )
        return await r.fetchall()


async def get_weekly_trend(user_id: int) -> list[dict]:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT gs.day::date AS day,
                   COALESCE(SUM(t.amount) FILTER (WHERE t.type='income'),  0) AS income,
                   COALESCE(SUM(t.amount) FILTER (WHERE t.type='expense'), 0) AS expense
            FROM generate_series(
                CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE, INTERVAL '1 day'
            ) gs(day)
            LEFT JOIN transactions t
                ON t.user_id=%s AND t.created_at::date=gs.day::date
            GROUP BY gs.day ORDER BY gs.day
            """,
            (user_id,),
        )
        return await r.fetchall()


async def get_stats_summary(user_id: int, year: int, month: int) -> dict:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            WITH daily AS (
                SELECT created_at::date AS day,
                       SUM(amount) FILTER (WHERE type='income')  AS inc,
                       SUM(amount) FILTER (WHERE type='expense') AS exp
                FROM transactions
                WHERE user_id=%s
                  AND EXTRACT(YEAR  FROM created_at)=%s
                  AND EXTRACT(MONTH FROM created_at)=%s
                GROUP BY created_at::date
            )
            SELECT
                COALESCE(AVG(inc), 0)::BIGINT AS avg_income_daily,
                COALESCE(AVG(exp), 0)::BIGINT AS avg_expense_daily,
                COALESCE(MAX(inc), 0)::BIGINT AS max_income_day,
                COALESCE(MAX(exp), 0)::BIGINT AS max_expense_day,
                COUNT(*) AS active_days
            FROM daily
            """,
            (user_id, year, month),
        )
        return await r.fetchone()


# ── Admin statistika ──────────────────────────────────────────────────────────

async def get_global_stats() -> dict:
    async with get_pool().connection() as conn:
        r = await conn.execute(
            """
            SELECT
                COUNT(DISTINCT t.user_id) AS active_users,
                COALESCE(SUM(t.amount) FILTER (WHERE t.type='income'),  0) AS total_income,
                COALESCE(SUM(t.amount) FILTER (WHERE t.type='expense'), 0) AS total_expense,
                COUNT(*) AS total_transactions
            FROM transactions t
            """
        )
        return await r.fetchone()
