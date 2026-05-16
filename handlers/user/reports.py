"""handlers/user/reports.py — Bugungi va oylik hisobotlar"""
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from services.finance_service import (
    get_today_summary, get_monthly_summary,
    get_category_breakdown, get_user_transactions,
    delete_last_transaction
)
from services.currency_service import fmt_uzs
from utils.keyboards import main_menu, confirm_keyboard

router = Router()

MONTHS_UZ = ["","Yanvar","Fevral","Mart","Aprel","May","Iyun",
              "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]


def balance_icon(b: int) -> str:
    return "📈" if b > 0 else "📉" if b < 0 else "⚖️"


@router.message(F.text == "📊 Bugungi hisobot")
async def today_report(message: Message) -> None:
    data = await get_today_summary(message.from_user.id)
    inc, exp = data["income"], data["expense"]
    bal = inc - exp
    today = datetime.now().strftime("%d.%m.%Y")
    await message.answer(
        f"📊 <b>Bugungi hisobot</b> — {today}\n"
        f"{'─'*28}\n"
        f"💰 Daromad:  <b>{fmt_uzs(inc)}</b>\n"
        f"💸 Harajat:  <b>{fmt_uzs(exp)}</b>\n"
        f"{'─'*28}\n"
        f"{balance_icon(bal)} Balans: <b>{fmt_uzs(abs(bal))}</b> "
        f"{'(+)' if bal >= 0 else '(-)'}\n"
        f"🔢 Tranzaksiyalar: {data['count']} ta",
        parse_mode="HTML", reply_markup=main_menu())


@router.message(F.text == "📅 Oylik hisobot")
async def monthly_report(message: Message) -> None:
    now = datetime.now()
    data = await get_monthly_summary(message.from_user.id, now.year, now.month)
    exp_cats = await get_category_breakdown(message.from_user.id, "expense", now.year, now.month)
    inc_cats = await get_category_breakdown(message.from_user.id, "income",  now.year, now.month)
    inc, exp = data["income"], data["expense"]
    bal = inc - exp

    def cats_text(rows):
        if not rows: return "   —\n"
        return "\n".join(f"   • {r['category']}: <b>{fmt_uzs(r['total'])}</b> ({r['cnt']} ta)" for r in rows) + "\n"

    await message.answer(
        f"📅 <b>{MONTHS_UZ[now.month]} {now.year} — Oylik hisobot</b>\n"
        f"{'─'*30}\n"
        f"💰 Daromad: <b>{fmt_uzs(inc)}</b>\n{cats_text(inc_cats)}"
        f"💸 Harajat: <b>{fmt_uzs(exp)}</b>\n{cats_text(exp_cats)}"
        f"{'─'*30}\n"
        f"{balance_icon(bal)} Balans: <b>{fmt_uzs(abs(bal))}</b> "
        f"{'(+)' if bal >= 0 else '(-)'}\n"
        f"🔢 Jami: {data['count']} ta",
        parse_mode="HTML", reply_markup=main_menu())


@router.message(F.text == "🕐 So'nggi tranzaksiyalar")
async def recent_tx(message: Message) -> None:
    rows = await get_user_transactions(message.from_user.id, limit=5)
    if not rows:
        await message.answer("📭 Hali tranzaksiyalar yo'q.", reply_markup=main_menu())
        return
    lines = ["🕐 <b>So'nggi 5 ta tranzaksiya:</b>\n"]
    for r in rows:
        icon = "💰" if r["type"] == "income" else "💸"
        note = f" — {r['note']}" if r.get("note") else ""
        lines.append(f"{icon} <b>{fmt_uzs(r['amount'])}</b> | {r['category']}{note}\n"
                     f"   🕒 {r['created_at'].strftime('%d.%m %H:%M')}")
    await message.answer("\n\n".join(lines), parse_mode="HTML", reply_markup=main_menu())


@router.message(F.text == "↩️ Bekor qilish")
async def undo_prompt(message: Message) -> None:
    await message.answer("⚠️ Oxirgi tranzaksiyani o'chirishni xohlaysizmi?",
                         reply_markup=confirm_keyboard("undo"))


@router.callback_query(F.data == "confirm:undo")
async def undo_confirm(callback: CallbackQuery) -> None:
    deleted = await delete_last_transaction(callback.from_user.id)
    if deleted:
        label = "Daromad" if deleted["type"] == "income" else "Harajat"
        await callback.message.edit_text(
            f"✅ O'chirildi: <b>{label}</b> — {fmt_uzs(deleted['amount'])}",
            parse_mode="HTML")
    else:
        await callback.message.edit_text("📭 O'chiriladigan tranzaksiya topilmadi.")
    await callback.answer()
