"""handlers/common/charts.py — Grafik va statistika"""
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from services.finance_service import (
    get_monthly_summary, get_category_breakdown,
    get_weekly_trend, get_stats_summary
)
from services.currency_service import get_rate, fmt_uzs, fmt_both
from services.ai_service import get_advice
from utils.charts import monthly_bar, category_pie, weekly_trend
from utils.keyboards import main_menu, chart_keyboard

router = Router()

MONTHS_UZ = ["","Yanvar","Fevral","Mart","Aprel","May","Iyun",
              "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]


@router.message(F.text == "📈 Grafik va statistika")
async def stats_menu(message: Message) -> None:
    now = datetime.now()
    await message.answer(
        f"📈 <b>Grafik va statistika</b> — {MONTHS_UZ[now.month]} {now.year}\n\nBirini tanlang:",
        parse_mode="HTML", reply_markup=chart_keyboard())


@router.callback_query(F.data == "chart:monthly")
async def chart_monthly(callback: CallbackQuery) -> None:
    await callback.answer("⏳ Tayyorlanmoqda...")
    now = datetime.now()
    d = await get_monthly_summary(callback.from_user.id, now.year, now.month)
    img = monthly_bar(d["income"], d["expense"], now.year, now.month)
    await callback.message.answer_photo(
        BufferedInputFile(img, "monthly.png"),
        caption=f"📊 {MONTHS_UZ[now.month]} {now.year} — Daromad vs Harajat",
        reply_markup=main_menu())


@router.callback_query(F.data == "chart:pie_expense")
async def chart_pie_exp(callback: CallbackQuery) -> None:
    await callback.answer("⏳ Tayyorlanmoqda...")
    now  = datetime.now()
    rows = await get_category_breakdown(callback.from_user.id, "expense", now.year, now.month)
    img  = category_pie(rows, "expense")
    if not img:
        await callback.message.answer("📭 Ma'lumot yo'q."); return
    await callback.message.answer_photo(
        BufferedInputFile(img, "pie_exp.png"),
        caption=f"💸 {MONTHS_UZ[now.month]} — Harajat kategoriyalari",
        reply_markup=main_menu())


@router.callback_query(F.data == "chart:pie_income")
async def chart_pie_inc(callback: CallbackQuery) -> None:
    await callback.answer("⏳ Tayyorlanmoqda...")
    now  = datetime.now()
    rows = await get_category_breakdown(callback.from_user.id, "income", now.year, now.month)
    img  = category_pie(rows, "income")
    if not img:
        await callback.message.answer("📭 Ma'lumot yo'q."); return
    await callback.message.answer_photo(
        BufferedInputFile(img, "pie_inc.png"),
        caption=f"💰 {MONTHS_UZ[now.month]} — Daromad kategoriyalari",
        reply_markup=main_menu())


@router.callback_query(F.data == "chart:weekly")
async def chart_weekly(callback: CallbackQuery) -> None:
    await callback.answer("⏳ Tayyorlanmoqda...")
    rows = await get_weekly_trend(callback.from_user.id)
    img  = weekly_trend(rows)
    if not img:
        await callback.message.answer("📭 Ma'lumot yo'q."); return
    await callback.message.answer_photo(
        BufferedInputFile(img, "weekly.png"),
        caption="📉 So'nggi 7 kunlik trend",
        reply_markup=main_menu())


@router.callback_query(F.data == "chart:stats")
async def text_stats(callback: CallbackQuery) -> None:
    now  = datetime.now()
    data = await get_stats_summary(callback.from_user.id, now.year, now.month)
    mo   = await get_monthly_summary(callback.from_user.id, now.year, now.month)
    rate = await get_rate("USD")
    inc, exp = mo["income"], mo["expense"]
    bal = inc - exp
    sign = "+" if bal >= 0 else "-"
    await callback.message.answer(
        f"🔢 <b>Statistika — {MONTHS_UZ[now.month]} {now.year}</b>\n{'─'*32}\n"
        f"💰 Daromad: <b>{fmt_both(inc, 'USD', rate)}</b>\n"
        f"💸 Harajat: <b>{fmt_both(exp, 'USD', rate)}</b>\n"
        f"⚖️ Balans:  <b>{sign}{fmt_both(abs(bal), 'USD', rate)}</b>\n"
        f"{'─'*32}\n"
        f"📆 Faol kunlar: <b>{data['active_days']}</b> ta\n"
        f"📈 O'rtacha kunlik daromad:\n   <b>{fmt_uzs(data['avg_income_daily'])}</b>\n"
        f"📉 O'rtacha kunlik harajat:\n   <b>{fmt_uzs(data['avg_expense_daily'])}</b>\n"
        f"🏆 Rekord daromad: <b>{fmt_uzs(data['max_income_day'])}</b>\n"
        f"🔴 Rekord harajat: <b>{fmt_uzs(data['max_expense_day'])}</b>",
        parse_mode="HTML", reply_markup=main_menu())
    await callback.answer()


async def _run_ai(callback: CallbackQuery) -> None:
    wait = await callback.message.answer(
        "🤖 <b>AI moliyaviy maslahatchi</b>\n\n⏳ Tahlil qilinmoqda...",
        parse_mode="HTML")
    now  = datetime.now()
    uid  = callback.from_user.id
    mo   = await get_monthly_summary(uid, now.year, now.month)
    cats = await get_category_breakdown(uid, "expense", now.year, now.month)
    tr   = await get_weekly_trend(uid)
    advice = await get_advice(mo["income"], mo["expense"], cats, tr, callback.from_user.full_name)
    await wait.delete()
    await callback.message.answer(
        f"🤖 <b>AI Moliyaviy Maslahat</b>\n{'─'*30}\n\n{advice}",
        parse_mode="HTML", reply_markup=main_menu())


@router.callback_query(F.data == "chart:ai_advice")
async def chart_ai(callback: CallbackQuery) -> None:
    await callback.answer("🤖 AI tahlil qilmoqda...")
    await _run_ai(callback)


@router.message(F.text == "🤖 AI maslahat")
async def ai_from_menu(message: Message) -> None:
    wait = await message.answer("🤖 <b>AI moliyaviy maslahatchi</b>\n\n⏳ Tahlil qilinmoqda...",
                                parse_mode="HTML")
    now  = datetime.now()
    uid  = message.from_user.id
    mo   = await get_monthly_summary(uid, now.year, now.month)
    cats = await get_category_breakdown(uid, "expense", now.year, now.month)
    tr   = await get_weekly_trend(uid)
    advice = await get_advice(mo["income"], mo["expense"], cats, tr, message.from_user.full_name)
    await wait.delete()
    await message.answer(
        f"🤖 <b>AI Moliyaviy Maslahat</b>\n{'─'*30}\n\n{advice}",
        parse_mode="HTML", reply_markup=main_menu())
