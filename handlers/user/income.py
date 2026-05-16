"""handlers/user/income.py — Daromad qo'shish"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.user_service import get_user
from services.finance_service import get_categories, add_transaction
from services.currency_service import get_rate, to_tiyin, fmt_uzs, fmt_both
from utils.keyboards import main_menu, category_keyboard, currency_keyboard
from utils.states import IncomeForm

router = Router()

MENU = {
    "💰 Daromad qo'shish","💸 Harajat qo'shish","📊 Bugungi hisobot",
    "📅 Oylik hisobot","📈 Grafik va statistika","🤖 AI maslahat",
    "✏️ Tranzaksiyalar","💱 Valyuta kursi","↩️ Bekor qilish",
}


@router.message(F.text == "💰 Daromad qo'shish")
async def income_start(message: Message, state: FSMContext) -> None:
    u = await get_user(message.from_user.id)
    if not u or not u.get("is_registered"):
        await message.answer("⚠️ Avval /start bilan ro'yxatdan o'ting.")
        return
    await state.clear()
    await state.set_state(IncomeForm.currency)
    await message.answer("💰 <b>Daromad qo'shish</b>\n\nValyutani tanlang:",
                         parse_mode="HTML", reply_markup=currency_keyboard())


@router.callback_query(IncomeForm.currency, F.data.startswith("currency:"))
async def income_currency(callback: CallbackQuery, state: FSMContext) -> None:
    currency = callback.data.split(":")[1]
    rate = await get_rate(currency) if currency != "UZS" else 100
    await state.update_data(currency=currency, rate=rate)
    hints = {"UZS":"500000","USD":"50.5","EUR":"45.0"}
    syms  = {"UZS":"so'm","USD":"$","EUR":"€"}
    rate_info = f"  (1 {currency} ≈ {rate//100:,} so'm)".replace(",", " ") if currency != "UZS" else ""
    await state.set_state(IncomeForm.amount)
    await callback.message.edit_text(
        f"💰 Miqdorni kiriting ({syms[currency]}):\n\n"
        f"<i>Masalan: {hints[currency]}{rate_info}</i>", parse_mode="HTML")
    await callback.answer()


@router.message(IncomeForm.amount)
async def income_amount(message: Message, state: FSMContext) -> None:
    if message.text in MENU:
        await state.clear()
        await message.answer("⚠️ Bekor qilindi.", reply_markup=main_menu())
        return
    try:
        val = float(message.text.replace(" ", "").replace(",", "."))
        assert val > 0
    except (ValueError, AssertionError):
        await message.answer("⚠️ To'g'ri son kiriting. Masalan: <b>500000</b>", parse_mode="HTML")
        return
    data = await state.get_data()
    currency, rate = data["currency"], data["rate"]
    amount_tiyin = to_tiyin(val, currency, rate)
    display = fmt_both(amount_tiyin, currency, rate)
    await state.update_data(amount=amount_tiyin, amount_orig=val, display=display)
    cats = await get_categories("income")
    await state.set_state(IncomeForm.category)
    await message.answer(f"✅ Miqdor: <b>{display}</b>\n\n📂 Kategoriyani tanlang:",
                         parse_mode="HTML", reply_markup=category_keyboard(cats, "income"))


@router.callback_query(IncomeForm.category, F.data.startswith("cat:income:"))
async def income_category(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, cat_id, cat_name = callback.data.split(":", 3)
    await state.update_data(category_id=int(cat_id), category_name=cat_name)
    await state.set_state(IncomeForm.note)
    await callback.message.edit_text(
        f"📂 Kategoriya: <b>{cat_name}</b>\n\n📝 Izoh kiriting yoki <b>—</b> yozing:",
        parse_mode="HTML")
    await callback.answer()


@router.message(IncomeForm.note)
async def income_note(message: Message, state: FSMContext) -> None:
    if message.text in MENU:
        await state.clear()
        await message.answer("⚠️ Bekor qilindi.", reply_markup=main_menu())
        return
    note = "" if message.text in ("—", "-") else message.text
    data = await state.get_data()
    await add_transaction(
        user_id=message.from_user.id, type_="income",
        amount=data["amount"], currency=data["currency"],
        amount_original=data["amount_orig"],
        category_id=data["category_id"], note=note)
    await state.clear()
    await message.answer(
        f"✅ <b>Daromad saqlandi!</b>\n\n"
        f"💰 {data['display']}\n"
        f"📂 {data['category_name']}\n"
        f"📝 {note or '—'}",
        parse_mode="HTML", reply_markup=main_menu())


@router.callback_query(F.data == "cancel")
async def cancel_cb(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()
