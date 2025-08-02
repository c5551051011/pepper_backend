# app/schemas/user.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., regex=r'^010-\d{4}-\d{4}$')
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, regex=r'^(MALE|FEMALE|OTHER)$')
    email: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PhoneVerificationRequest(BaseModel):
    phone_number: str = Field(..., regex=r'^010-\d{4}-\d{4}$')


class PhoneVerificationConfirm(BaseModel):
    phone_number: str = Field(..., regex=r'^010-\d{4}-\d{4}$')
    verification_code: str = Field(..., regex=r'^\d{6}$')


# app/schemas/wallet.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class WalletBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=100)
    is_shared: bool = False


class WalletCreate(WalletBase):
    store_id: UUID


class WalletResponse(WalletBase):
    id: UUID
    status: str
    balance: Decimal
    bonus_balance: Decimal
    owner_id: UUID
    store_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    type: str = Field(..., regex=r'^(CHARGE|SPEND|BONUS_EARNED|REFUND)$')
    method: str = Field(..., regex=r'^(CARD|CASH|EXTERNAL_APP|TRANSFER)$')
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: UUID
    type: str
    method: str
    wallet_id: UUID
    amount: Decimal
    fee_amount: Decimal
    balance_after_transaction: Decimal
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True