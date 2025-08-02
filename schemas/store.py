# app/schemas/store.py
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class StoreLocationBase(BaseModel):
    address: str
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    region: Optional[str] = None
    postal_code: Optional[str] = None


class StoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., regex=r'^(RESTAURANT|CAFE|SALON|NAILSHOP|CONVENIENCE_STORE|OTHER)$')
    business_registration_number: Optional[str] = None


class StoreCreate(StoreBase):
    location: StoreLocationBase


class StoreResponse(StoreBase):
    id: UUID
    is_active: bool
    created_at: datetime
    location: Optional[StoreLocationBase]

    class Config:
        from_attributes = True