"""
services/currency_service.py — Valyuta kurslari va konvertatsiya (CBU API)
"""
from __future__ import annotations
import httpx
from datetime import date
from core.config import DEFAULT_USD_TO_UZS, DEFAULT_EUR_TO_UZS

_cache: dict[str, dict[date, int]] = {}


async def get_rate(code: str) -> int:
    """CBU dan valyuta kursi (tiyin). Kunlik kesh."""
    today = date.today()
    if today in _cache.get(code, {}):
        return _cache[code][today]

    defaults = {
        "USD": DEFAULT_USD_TO_UZS * 100,
        "EUR": DEFAULT_EUR_TO_UZS * 100,
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"https://cbu.uz/uz/arkhiv-kursov-valyut/json/{code}/")
            rate_tiyin = int(float(r.json()[0]["Rate"])) * 100
            _cache.setdefault(code, {})[today] = rate_tiyin
            return rate_tiyin
    except Exception:
        return defaults.get(code, DEFAULT_USD_TO_UZS * 100)


def to_tiyin(amount: float, currency: str, rate: int) -> int:
    if currency == "UZS":
        return int(amount) * 100
    return int(amount * rate)


def fmt_uzs(tiyin: int) -> str:
    return f"{tiyin // 100:,}".replace(",", " ") + " so'm"

def fmt_currency(tiyin: int, currency: str, rate: int) -> str:
    if currency == "USD":
        return f"${tiyin / rate:,.2f}"
    if currency == "EUR":
        return f"€{tiyin / rate:,.2f}"
    return fmt_uzs(tiyin)

def fmt_both(tiyin: int, currency: str, rate: int) -> str:
    uzs = fmt_uzs(tiyin)
    if currency in ("USD", "EUR"):
        return f"{uzs}  (~{fmt_currency(tiyin, currency, rate)})"
    return uzs
