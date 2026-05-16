"""
services/ai_service.py — Google Gemini AI maslahat xizmati
"""
from __future__ import annotations
import asyncio
from core.config import GEMINI_API_KEY
from services.currency_service import fmt_uzs


def _build_prompt(income: int, expense: int, cats: list[dict],
                  trend: list[dict], name: str) -> str:
    balance = income - expense
    pct = (balance / income * 100) if income > 0 else 0

    cats_text = "\n".join(
        f"  - {r['category']}: {fmt_uzs(r['total'])} "
        f"({r['total']/expense*100:.1f}%)" if expense > 0 else f"  - {r['category']}: {fmt_uzs(r['total'])}"
        for r in cats
    ) or "  Ma'lumot yo'q"

    trend_text = "\n".join(
        f"  {r['day'].strftime('%d.%m')}: daromad {fmt_uzs(r['income'])}, harajat {fmt_uzs(r['expense'])}"
        for r in trend
    ) or "  Ma'lumot yo'q"

    return f"""
Siz tajribali moliyaviy maslahatchi yordamchisisiz. Foydalanuvchi: {name}.

Joriy oy:
- Daromad: {fmt_uzs(income)}
- Harajat: {fmt_uzs(expense)}
- Balans: {fmt_uzs(balance)} ({'tejash' if balance >= 0 else 'kamomad'})
- Tejash darajasi: {pct:.1f}%

Harajat kategoriyalari:
{cats_text}

So'nggi 7 kun:
{trend_text}

Javob tuzilmasi (Telegram HTML: <b>, <i>):

<b>📊 Moliyaviy holat</b>
(1-2 gapda baholash)

<b>⚠️ Kamaytirishga tavsiyalar</b>
(eng katta 2-3 kategoriya, aniq so'm/foiz)

<b>💡 50/30/20 qoidasi</b>
(zaruriy/xohish/tejash moslash)

<b>🎯 Keyingi oy uchun 3 maqsad</b>
1. ...
2. ...
3. ...

Faqat o'zbek tilida, ixcham va aniq.
""".strip()


async def get_advice(income: int, expense: int, cats: list[dict],
                     trend: list[dict], user_name: str) -> str:
    if not GEMINI_API_KEY:
        return (
            "⚠️ <b>AI xizmati ulangmagan.</b>\n\n"
            "Faollashtirish:\n"
            "1. <a href='https://aistudio.google.com/apikey'>aistudio.google.com</a>\n"
            "2. API kalit oling (bepul)\n"
            "3. <code>.env</code> ga: <code>GEMINI_API_KEY=...</code>"
        )
    if expense == 0:
        return "📭 Harajat ma'lumotlari yo'q. Avval harajat kiriting."

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = _build_prompt(income, expense, cats, trend, user_name)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
        return response.text
    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper():
            return "❌ <b>API kalit noto'g'ri.</b> <code>.env</code> ni tekshiring."
        if "quota" in err.lower():
            return "⏳ <b>Kunlik limit tugadi.</b> Ertaga qayta urinib ko'ring."
        return f"❌ <b>Xatolik:</b> {err[:200]}"
