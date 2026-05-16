"""handlers/admin/block.py — Bloklash va admin berish"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from services.user_service import get_user, set_blocked, set_admin, is_admin
from utils.keyboards import user_action_keyboard

router = Router()


@router.callback_query(F.data.startswith("admin:toggle_block:"))
async def toggle_block(callback: CallbackQuery) -> None:
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q.", show_alert=True); return
    target_id = int(callback.data.split(":")[2])
    if target_id == callback.from_user.id:
        await callback.answer("⚠️ O'zingizni bloklay olmaysiz!", show_alert=True); return
    u = await get_user(target_id)
    if not u:
        await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True); return
    new_blocked = not u["is_blocked"]
    await set_blocked(target_id, new_blocked)
    action = "🚫 Bloklandi" if new_blocked else "✅ Razblok qilindi"
    await callback.answer(f"{u['full_name'] or str(target_id)}: {action}", show_alert=True)
    updated = await get_user(target_id)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=user_action_keyboard(target_id, updated["is_blocked"], updated["is_admin"]))
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin:make_admin:"))
async def make_admin(callback: CallbackQuery) -> None:
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q.", show_alert=True); return
    target_id = int(callback.data.split(":")[2])
    await set_admin(target_id, True)
    await callback.answer("👑 Admin qilindi!", show_alert=True)
    updated = await get_user(target_id)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=user_action_keyboard(target_id, updated["is_blocked"], updated["is_admin"]))
    except Exception:
        pass
