"""handlers/admin/users.py — Foydalanuvchilar ro'yxati va boshqaruv"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from services.user_service import get_all_users, get_users_count, get_user, set_blocked, set_admin, is_admin
from utils.keyboards import admin_menu, user_action_keyboard

router = Router()


@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message) -> None:
    if not await is_admin(message.from_user.id): return
    counts = await get_users_count()
    users  = await get_all_users(limit=10)
    lines  = [
        f"👥 <b>Foydalanuvchilar</b>\n"
        f"Jami: <b>{counts['total']}</b> | "
        f"Ro'yxatdan: <b>{counts['registered']}</b> | "
        f"Bloklangan: <b>{counts['blocked']}</b>\n{'─'*28}"
    ]
    for u in users:
        st = "🚫" if u["is_blocked"] else ("👑" if u["is_admin"] else "✅" if u["is_registered"] else "⏳")
        uname = f"@{u['username']}" if u["username"] else "—"
        lines.append(
            f"{st} <b>{u['full_name'] or '—'}</b> ({uname})\n"
            f"   📱 {u['phone'] or '—'} | ID: <code>{u['id']}</code>"
        )
    await message.answer("\n\n".join(lines), parse_mode="HTML", reply_markup=admin_menu())


@router.message(F.text.startswith("/user "))
async def admin_find_user(message: Message) -> None:
    if not await is_admin(message.from_user.id): return
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Foydalanish: <code>/user 123456789</code>", parse_mode="HTML"); return
    u = await get_user(target_id)
    if not u:
        await message.answer("❌ Foydalanuvchi topilmadi."); return
    st  = "🚫 Bloklangan" if u["is_blocked"] else ("👑 Admin" if u["is_admin"] else "✅ Faol")
    reg = "Ha ✅" if u["is_registered"] else "Yo'q ⏳"
    await message.answer(
        f"👤 <b>{u['full_name']}</b>\n"
        f"Username: @{u['username'] or '—'}\n"
        f"ID: <code>{u['id']}</code>\n"
        f"📱 Tel: {u['phone'] or '—'}\n"
        f"Status: {st}\n"
        f"Ro'yxatdan: {reg}\n"
        f"Qo'shilgan: {u['created_at'].strftime('%d.%m.%Y')}",
        parse_mode="HTML",
        reply_markup=user_action_keyboard(target_id, u["is_blocked"], u["is_admin"]))
