# 💰 Finance Bot v2 — Senior Structure

## Papka strukturasi
```
finance_bot_v2/
├── bot.py                      # Asosiy kirish nuqtasi
├── init_db.sql                 # DB sxemasi
├── migrate_v2.sql              # Mavjud DB migration
├── requirements.txt
├── .env.example
│
├── core/                       # Asosiy infratuzilma
│   ├── config.py               # Sozlamalar (.env)
│   ├── database.py             # DB pool (psycopg3)
│   └── models.py               # Dataclass modellari
│
├── services/                   # Biznes logika
│   ├── user_service.py         # Foydalanuvchi CRUD
│   ├── finance_service.py      # Tranzaksiya, hisobot
│   ├── currency_service.py     # Kurs, konvertatsiya
│   └── ai_service.py           # Gemini AI maslahat
│
├── handlers/                   # Telegram handlerlar
│   ├── user/                   # Foydalanuvchi
│   │   ├── start.py            # /start, ro'yxatdan o'tish
│   │   ├── income.py           # Daromad qo'shish
│   │   ├── expense.py          # Harajat qo'shish
│   │   ├── reports.py          # Bugungi/oylik hisobot
│   │   └── transactions.py     # Ko'rish, tahrirlash, o'chirish
│   ├── admin/                  # Admin panel
│   │   ├── users.py            # Foydalanuvchilar ro'yxati
│   │   ├── block.py            # Bloklash/razblok, admin berish
│   │   └── stats.py            # Global statistika
│   └── common/                 # Umumiy
│       ├── currency.py         # Valyuta kursi
│       └── charts.py           # Grafik, statistika, AI
│
├── utils/                      # Yordamchi
│   ├── keyboards.py            # Barcha tugmalar
│   ├── states.py               # FSM state lar
│   └── charts.py               # Matplotlib grafiklar
│
└── middlewares/                # Middleware
    └── user_middleware.py      # Foydalanuvchi saqlash, bloklash
```

## O'rnatish
```bash
pip install -r requirements.txt
psql -U postgres -c "CREATE DATABASE finance_bot;"
psql -U postgres -d finance_bot -f init_db.sql
cp .env.example .env
python bot.py
```
