"""
core/models.py — Ma'lumot modellari (dataclass)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    username: Optional[str]
    full_name: str
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_registered: bool = False
    is_blocked: bool = False
    is_admin: bool = False
    created_at: Optional[datetime] = None


@dataclass
class Transaction:
    id: int
    user_id: int
    type: str          # 'income' | 'expense'
    amount: int        # tiyin
    currency: str      # 'UZS' | 'USD' | 'EUR'
    amount_original: Optional[float]
    category_id: int
    note: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Category:
    id: int
    name: str
    type: str          # 'income' | 'expense'
