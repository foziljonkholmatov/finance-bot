"""
core/config.py — Barcha sozlamalar (.env dan)
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Bot ───────────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

# ── PostgreSQL ────────────────────────────────────────────────────────────────
DB_HOST:     str = os.getenv("DB_HOST", "localhost")
DB_PORT:     int = int(os.getenv("DB_PORT", 5432))
DB_NAME:     str = os.getenv("DB_NAME", "finance_bot")
DB_USER:     str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

DB_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ── AI ────────────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# ── Valyuta (fallback kurslar) ────────────────────────────────────────────────
DEFAULT_USD_TO_UZS: int = 12_700
DEFAULT_EUR_TO_UZS: int = 13_800
