"""
bot.py — Asosiy kirish nuqtasi
"""
import asyncio
import logging
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import BOT_TOKEN
from core.database import init_pool, close_pool
from middlewares.user_middleware import UserMiddleware

# User handlerlari
from handlers.user.start        import router as start_router
from handlers.user.income       import router as income_router
from handlers.user.expense      import router as expense_router
from handlers.user.reports      import router as reports_router
from handlers.user.transactions import router as tx_router

# Admin handlerlari
from handlers.admin.users  import router as admin_users_router
from handlers.admin.block  import router as admin_block_router
from handlers.admin.stats  import router as admin_stats_router

# Umumiy handlerlari
from handlers.common.currency import router as currency_router
from handlers.common.charts   import router as charts_router


async def main() -> None:
    await init_pool()
    logger.info("✅ PostgreSQL pool tayyor")

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    # Middleware
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # User routerlar
    dp.include_router(start_router)
    dp.include_router(income_router)
    dp.include_router(expense_router)
    dp.include_router(reports_router)
    dp.include_router(tx_router)

    # Admin routerlar
    dp.include_router(admin_users_router)
    dp.include_router(admin_block_router)
    dp.include_router(admin_stats_router)

    # Umumiy routerlar
    dp.include_router(currency_router)
    dp.include_router(charts_router)

    logger.info("🚀 Bot ishga tushdi!")
    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()
        await bot.session.close()
        logger.info("👋 Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
