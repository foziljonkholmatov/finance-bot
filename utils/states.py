"""
utils/states.py — Barcha FSM state lar bitta joyda
"""
from aiogram.fsm.state import State, StatesGroup


class RegForm(StatesGroup):
    phone    = State()
    location = State()


class IncomeForm(StatesGroup):
    currency = State()
    amount   = State()
    category = State()
    note     = State()


class ExpenseForm(StatesGroup):
    currency = State()
    amount   = State()
    category = State()
    note     = State()


class EditTxForm(StatesGroup):
    amount = State()
    note   = State()
