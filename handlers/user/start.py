"""handlers/user/start.py — /start va ro'yxatdan o'tish"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

from core.config import ADMIN_IDS
from services.user_service import get_user, set_admin, complete_registration
from utils.keyboards import main_menu, admin_menu, registration_phone_kb, registration_location_kb
from utils.states import RegForm

router = Router()

MENU = {
    "💰 Daromad qo'shish","💸 Harajat qo'shish","📊 Bugungi hisobot",
    "📅 Oylik hisobot","📈 Grafik va statistika","🤖 AI maslahat",
    "✏️ Tranzaksiyalar","💱 Valyuta kursi","↩️ Bekor qilish",
}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    uid = message.from_user.id
    if uid in ADMIN_IDS:
        await set_admin(uid, True)
    u = await get_user(uid)
    if u and u.get("is_admin"):
        await message.answer(
            f"👑 Xush kelibsiz, Admin <b>{message.from_user.full_name}</b>!",
            reply_markup=admin_menu(), parse_mode="HTML")
        return
    if u and u.get("is_registered"):
        await message.answer(
            f"👋 Xush kelibsiz, <b>{message.from_user.full_name}</b>!",
            reply_markup=main_menu(), parse_mode="HTML")
        return
    await state.set_state(RegForm.phone)
    await message.answer(
        f"👋 Salom, <b>{message.from_user.full_name}</b>!\n\n"
        "Botdan foydalanish uchun ro'yxatdan o'ting.\n\n"
        "📱 <b>1-qadam:</b> Telefon raqamingizni yuboring:",
        parse_mode="HTML", reply_markup=registration_phone_kb())


@router.message(RegForm.phone, F.content_type == ContentType.CONTACT)
async def reg_phone(message: Message, state: FSMContext) -> None:
    if message.contact.user_id != message.from_user.id:
        await message.answer("⚠️ O'z telefon raqamingizni yuboring.")
        return
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(RegForm.location)
    await message.answer(
        "✅ Telefon qabul qilindi!\n\n📍 <b>2-qadam:</b> Joylashuvingizni yuboring:",
        parse_mode="HTML", reply_markup=registration_location_kb())


@router.message(RegForm.phone)
async def reg_phone_wrong(message: Message) -> None:
    await message.answer("⚠️ Tugma orqali telefon raqamingizni yuboring.",
                         reply_markup=registration_phone_kb())


@router.message(RegForm.location, F.content_type == ContentType.LOCATION)
async def reg_location(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    loc  = message.location
    await complete_registration(message.from_user.id, data["phone"], loc.latitude, loc.longitude)
    await state.clear()
    await message.answer(
        "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>\n\n"
        f"📱 Telefon: <code>{data['phone']}</code>\n"
        f"📍 Joylashuv saqlandi\n\n"
        "Endi botdan to'liq foydalanishingiz mumkin:",
        parse_mode="HTML", reply_markup=main_menu())


@router.message(RegForm.location)
async def reg_location_wrong(message: Message) -> None:
    await message.answer("⚠️ Tugma orqali joylashuvingizni yuboring.",
                         reply_markup=registration_location_kb())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    u = await get_user(message.from_user.id)
    kb = admin_menu() if (u and u.get("is_admin")) else main_menu()
    await message.answer("❌ Bekor qilindi.", reply_markup=kb)


@router.message(F.text == "🔙 User rejimiga qaytish")
async def back_to_user(message: Message) -> None:
    await message.answer("👤 User rejimi:", reply_markup=main_menu())
