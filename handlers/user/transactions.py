"""handlers/user/transactions.py — Tranzaksiyalarni ko'rish, tahrirlash, o'chirish"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.finance_service import (
    get_user_transactions, get_transaction,
    update_transaction_amount, update_transaction_note, delete_transaction
)
from services.currency_service import get_rate, to_tiyin, fmt_uzs, fmt_both
from utils.keyboards import main_menu, tx_list_keyboard, tx_action_keyboard, confirm_delete_keyboard
from utils.states import EditTxForm

router = Router()

MENU = {
    "💰 Daromad qo'shish","💸 Harajat qo'shish","📊 Bugungi hisobot",
    "📅 Oylik hisobot","📈 Grafik va statistika","🤖 AI maslahat",
    "✏️ Tranzaksiyalar","💱 Valyuta kursi","↩️ Bekor qilish",
}


def tx_text(tx: dict) -> str:
    icon  = "💰" if tx["type"] == "income" else "💸"
    label = "Daromad" if tx["type"] == "income" else "Harajat"
    cur   = tx.get("currency", "UZS")
    orig  = tx.get("amount_original")
    extra = ""
    if cur != "UZS" and orig:
        sym = "$" if cur == "USD" else "€"
        extra = f" ({sym}{orig:.2f})"
    return (
        f"{icon} <b>{label}</b> #{tx['id']}\n"
        f"💵 {fmt_uzs(tx['amount'])}{extra}\n"
        f"📂 {tx['category']}\n"
        f"📝 {tx['note'] or '—'}\n"
        f"🕒 {tx['created_at'].strftime('%d.%m.%Y %H:%M')}"
    )


async def _show_list(target, user_id: int, offset: int, edit: bool = True) -> None:
    rows = await get_user_transactions(user_id, limit=5, offset=offset)
    if not rows:
        text = "📭 Hali tranzaksiyalar yo'q."
        if edit and hasattr(target, "edit_text"):
            await target.edit_text(text)
        else:
            await target.answer(text, reply_markup=main_menu())
        return
    all_rows = await get_user_transactions(user_id, limit=1000)
    total = len(all_rows)
    text  = f"📋 <b>Tranzaksiyalar</b> ({offset+1}–{min(offset+5, total)} / {total})\n\nBirini tanlang:"
    kb    = tx_list_keyboard(rows, offset, total)
    if edit and hasattr(target, "edit_text"):
        await target.edit_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=kb)


@router.message(F.text == "✏️ Tranzaksiyalar")
async def tx_list(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _show_list(message, message.from_user.id, offset=0, edit=False)


@router.callback_query(F.data.startswith("tx:page:"))
async def tx_page(callback: CallbackQuery) -> None:
    offset = int(callback.data.split(":")[2])
    await _show_list(callback.message, callback.from_user.id, offset, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("tx:view:"))
async def tx_view(callback: CallbackQuery) -> None:
    tx_id = int(callback.data.split(":")[2])
    tx = await get_transaction(tx_id, callback.from_user.id)
    if not tx:
        await callback.answer("❌ Topilmadi.", show_alert=True); return
    await callback.message.edit_text(
        tx_text(tx) + "\n\n✏️ Nima qilmoqchisiz?",
        parse_mode="HTML", reply_markup=tx_action_keyboard(tx_id))
    await callback.answer()


@router.callback_query(F.data == "tx:back")
async def tx_back(callback: CallbackQuery) -> None:
    await _show_list(callback.message, callback.from_user.id, 0, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("tx:edit_amount:"))
async def tx_edit_amount_start(callback: CallbackQuery, state: FSMContext) -> None:
    tx_id = int(callback.data.split(":")[2])
    tx = await get_transaction(tx_id, callback.from_user.id)
    if not tx:
        await callback.answer("❌ Topilmadi.", show_alert=True); return
    await state.set_state(EditTxForm.amount)
    await state.update_data(tx_id=tx_id, currency=tx.get("currency","UZS"))
    sym = {"UZS":"so'm","USD":"$","EUR":"€"}[tx.get("currency","UZS")]
    await callback.message.edit_text(
        f"✏️ Yangi miqdorni kiriting ({sym}):\n\nHozirgi: <b>{fmt_uzs(tx['amount'])}</b>",
        parse_mode="HTML")
    await callback.answer()


@router.message(EditTxForm.amount)
async def tx_edit_amount_save(message: Message, state: FSMContext) -> None:
    if message.text in MENU:
        await state.clear()
        await message.answer("⚠️ Bekor qilindi.", reply_markup=main_menu()); return
    try:
        val = float(message.text.replace(" ","").replace(",","."))
        assert val > 0
    except (ValueError, AssertionError):
        await message.answer("⚠️ To'g'ri son kiriting."); return
    data = await state.get_data()
    cur  = data["currency"]
    rate = await get_rate(cur) if cur != "UZS" else 100
    tiyin = to_tiyin(val, cur, rate)
    ok = await update_transaction_amount(data["tx_id"], message.from_user.id, tiyin, val, cur)
    await state.clear()
    if ok:
        await message.answer(f"✅ Miqdor yangilandi: <b>{fmt_both(tiyin, cur, rate)}</b>",
                             parse_mode="HTML", reply_markup=main_menu())
    else:
        await message.answer("❌ Xatolik yuz berdi.", reply_markup=main_menu())


@router.callback_query(F.data.startswith("tx:edit_note:"))
async def tx_edit_note_start(callback: CallbackQuery, state: FSMContext) -> None:
    tx_id = int(callback.data.split(":")[2])
    tx = await get_transaction(tx_id, callback.from_user.id)
    if not tx:
        await callback.answer("❌ Topilmadi.", show_alert=True); return
    await state.set_state(EditTxForm.note)
    await state.update_data(tx_id=tx_id)
    await callback.message.edit_text(
        f"📝 Yangi izoh kiriting:\n\nHozirgi: <i>{tx['note'] or '—'}</i>",
        parse_mode="HTML")
    await callback.answer()


@router.message(EditTxForm.note)
async def tx_edit_note_save(message: Message, state: FSMContext) -> None:
    if message.text in MENU:
        await state.clear()
        await message.answer("⚠️ Bekor qilindi.", reply_markup=main_menu()); return
    data = await state.get_data()
    note = "" if message.text in ("—","-") else message.text
    ok = await update_transaction_note(data["tx_id"], message.from_user.id, note)
    await state.clear()
    await message.answer("✅ Izoh yangilandi." if ok else "❌ Xatolik.", reply_markup=main_menu())


@router.callback_query(F.data.startswith("tx:delete:"))
async def tx_delete_confirm(callback: CallbackQuery) -> None:
    tx_id = int(callback.data.split(":")[2])
    tx = await get_transaction(tx_id, callback.from_user.id)
    if not tx:
        await callback.answer("❌ Topilmadi.", show_alert=True); return
    await callback.message.edit_text(
        f"🗑 <b>O'chirishni tasdiqlaysizmi?</b>\n\n{tx_text(tx)}",
        parse_mode="HTML", reply_markup=confirm_delete_keyboard(tx_id))
    await callback.answer()


@router.callback_query(F.data.startswith("tx:confirm_delete:"))
async def tx_delete_do(callback: CallbackQuery) -> None:
    tx_id = int(callback.data.split(":")[2])
    ok = await delete_transaction(tx_id, callback.from_user.id)
    if ok:
        await callback.message.edit_text("✅ Tranzaksiya o'chirildi.")
        await callback.answer("O'chirildi!")
    else:
        await callback.answer("❌ Xatolik.", show_alert=True)
