"""handlers/common/currency.py — Valyuta kursi ko'rsatish"""
from aiogram import Router, F
from aiogram.types import Message
from services.currency_service import get_rate
from utils.keyboards import main_menu

router = Router()

@router.message(F.text == "💱 Valyuta kursi")
async def exchange_rate(message: Message) -> None:
    usd = await get_rate("USD")
    eur = await get_rate("EUR")
    usd_fmt = f"{usd // 100:,}".replace(",", " ")
    eur_fmt = f"{eur // 100:,}".replace(",", " ")
    await message.answer(
        f"💱 <b>Valyuta kursi (CBU)</b>\n\n"
        f"🇺🇸 1 USD = <b>{usd_fmt} so'm</b>\n"
        f"🇪🇺 1 EUR = <b>{eur_fmt} so'm</b>\n\n"
        f"<i>Markaziy bank (cbu.uz) dan olinadi</i>",
        parse_mode="HTML", reply_markup=main_menu())
