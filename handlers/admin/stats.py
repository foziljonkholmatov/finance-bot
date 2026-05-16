"""handlers/admin/stats.py — Global statistika va user statistikasi"""
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from services.user_service import get_users_count, get_user, is_admin
from services.finance_service import get_global_stats, get_monthly_summary
from services.currency_service import fmt_uzs
from utils.keyboards import admin_menu

router = Router()

MONTHS_UZ = ["","Yanvar","Fevral","Mart","Aprel","May","Iyun",
              "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]


@router.message(F.text == "📊 Global statistika")
async def global_stats(message: Message) -> None:
    if not await is_admin(message.from_user.id): return
    stats  = await get_global_stats()
    counts = await get_users_count()
    bal = stats["total_income"] - stats["total_expense"]
    await message.answer(
        f"📊 <b>Global statistika</b>\n{'─'*28}\n"
        f"👥 Jami userlar:    <b>{counts['total']}</b>\n"
        f"   ✅ Ro'yxatdan:   <b>{counts['registered']}</b>\n"
        f"   🚫 Bloklangan:   <b>{counts['blocked']}</b>\n"
        f"{'─'*28}\n"
        f"💰 Jami daromad:   <b>{fmt_uzs(stats['total_income'])}</b>\n"
        f"💸 Jami harajat:   <b>{fmt_uzs(stats['total_expense'])}</b>\n"
        f"⚖️ Balans:         <b>{fmt_uzs(abs(bal))} {'(+)' if bal>=0 else '(-)'}</b>\n"
        f"🔢 Tranzaksiyalar: <b>{stats['total_transactions']}</b> ta\n"
        f"👤 Faol userlar:   <b>{stats['active_users']}</b>",
        parse_mode="HTML", reply_markup=admin_menu())


@router.callback_query(F.data.startswith("admin:user_stats:"))
async def user_stats(callback: CallbackQuery) -> None:
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q.", show_alert=True); return
    now = datetime.now()
    target_id = int(callback.data.split(":")[2])
    u = await get_user(target_id)
    m = await get_monthly_summary(target_id, now.year, now.month)
    bal = m["income"] - m["expense"]
    name = u["full_name"] if u else str(target_id)
    await callback.message.answer(
        f"📊 <b>{name}</b> — {MONTHS_UZ[now.month]} {now.year}\n{'─'*26}\n"
        f"💰 Daromad: <b>{fmt_uzs(m['income'])}</b>\n"
        f"💸 Harajat: <b>{fmt_uzs(m['expense'])}</b>\n"
        f"⚖️ Balans:  <b>{fmt_uzs(abs(bal))} {'(+)' if bal>=0 else '(-)'}</b>\n"
        f"🔢 Tranzaksiyalar: {m['count']} ta",
        parse_mode="HTML")
    await callback.answer()
