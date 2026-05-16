"""
utils/keyboards.py — Barcha Telegram tugmalari
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="💰 Daromad qo'shish"),
          KeyboardButton(text="💸 Harajat qo'shish"))
    b.row(KeyboardButton(text="📊 Bugungi hisobot"),
          KeyboardButton(text="📅 Oylik hisobot"))
    b.row(KeyboardButton(text="📈 Grafik va statistika"),
          KeyboardButton(text="🤖 AI maslahat"))
    b.row(KeyboardButton(text="✏️ Tranzaksiyalar"),
          KeyboardButton(text="💱 Valyuta kursi"))
    b.row(KeyboardButton(text="↩️ Bekor qilish"))
    return b.as_markup(resize_keyboard=True)


def admin_menu() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="👥 Foydalanuvchilar"),
          KeyboardButton(text="📊 Global statistika"))
    b.row(KeyboardButton(text="🔙 User rejimiga qaytish"))
    return b.as_markup(resize_keyboard=True)


def registration_phone_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)


def registration_location_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)


def currency_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🇺🇿 UZS (so'm)",   callback_data="currency:UZS")
    b.button(text="🇺🇸 USD (dollar)", callback_data="currency:USD")
    b.button(text="🇪🇺 EUR (euro)",   callback_data="currency:EUR")
    b.button(text="❌ Bekor",          callback_data="cancel")
    b.adjust(3, 1)
    return b.as_markup()


def category_keyboard(categories: list[dict], type_: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for cat in categories:
        b.button(text=cat["name"],
                 callback_data=f"cat:{type_}:{cat['id']}:{cat['name']}")
    b.button(text="❌ Bekor", callback_data="cancel")
    b.adjust(2)
    return b.as_markup()


def tx_list_keyboard(rows: list[dict], offset: int, total: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for tx in rows:
        icon  = "💰" if tx["type"] == "income" else "💸"
        date  = tx["created_at"].strftime("%d.%m")
        amt   = f"{tx['amount'] // 100:,}".replace(",", " ")
        b.button(
            text=f"{icon} {date} | {amt} so'm | {tx['category']}",
            callback_data=f"tx:view:{tx['id']}",
        )
    b.adjust(1)
    nav = []
    if offset > 0:
        nav.append(("⬅️ Oldingi", f"tx:page:{offset-5}"))
    if offset + 5 < total:
        nav.append(("Keyingi ➡️", f"tx:page:{offset+5}"))
    for label, data in nav:
        b.button(text=label, callback_data=data)
    return b.as_markup()


def tx_action_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Miqdorni o'zgartirish", callback_data=f"tx:edit_amount:{tx_id}")
    b.button(text="📝 Izohni o'zgartirish",   callback_data=f"tx:edit_note:{tx_id}")
    b.button(text="🗑 O'chirish",              callback_data=f"tx:delete:{tx_id}")
    b.button(text="◀️ Orqaga",                callback_data="tx:back")
    b.adjust(1)
    return b.as_markup()


def confirm_delete_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Ha, o'chir", callback_data=f"tx:confirm_delete:{tx_id}")
    b.button(text="❌ Yo'q",       callback_data=f"tx:view:{tx_id}")
    b.adjust(2)
    return b.as_markup()


def user_action_keyboard(user_id: int, is_blocked: bool, is_admin: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    block_text = "✅ Razblok qilish" if is_blocked else "🚫 Bloklash"
    b.button(text=block_text,          callback_data=f"admin:toggle_block:{user_id}")
    b.button(text="📊 Statistikasi",   callback_data=f"admin:user_stats:{user_id}")
    if not is_admin:
        b.button(text="👑 Admin qilish", callback_data=f"admin:make_admin:{user_id}")
    b.adjust(1)
    return b.as_markup()


def chart_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📊 Oylik daromad/harajat",  callback_data="chart:monthly")
    b.button(text="🥧 Harajat kategoriyalari", callback_data="chart:pie_expense")
    b.button(text="🥧 Daromad kategoriyalari", callback_data="chart:pie_income")
    b.button(text="📉 7 kunlik trend",          callback_data="chart:weekly")
    b.button(text="🔢 Statistika (matn)",       callback_data="chart:stats")
    b.button(text="🤖 AI maslahat",             callback_data="chart:ai_advice")
    b.adjust(1)
    return b.as_markup()


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Ha", callback_data=f"confirm:{action}")
    b.button(text="❌ Yo'q", callback_data="cancel")
    b.adjust(2)
    return b.as_markup()
