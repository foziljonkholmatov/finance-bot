"""
middlewares/user_middleware.py — Foydalanuvchini saqlash va bloklash tekshiruvi
"""
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from services.user_service import upsert_user, get_user


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user:
            await upsert_user(user.id, user.username, user.full_name)
            db_user = await get_user(user.id)

            if db_user and db_user["is_blocked"]:
                if isinstance(event, Message):
                    await event.answer("🚫 Siz bloklangansiz. Admin bilan bog'laning.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Siz bloklangansiz.", show_alert=True)
                return

        return await handler(event, data)
