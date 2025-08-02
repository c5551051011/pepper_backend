# app/models/user.py
from sqlalchemy import Column, String, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    email = Column(String(255))
    is_verified = Column(Boolean, default=False, index=True)

    # Relationships
    owned_wallets = relationship("Wallet", back_populates="owner", cascade="all, delete-orphan")
    wallet_memberships = relationship("WalletMember", back_populates="user")
    store_managements = relationship("StoreManager", back_populates="user")
    created_transactions = relationship("Transaction", foreign_keys="Transaction.created_by", back_populates="creator")
