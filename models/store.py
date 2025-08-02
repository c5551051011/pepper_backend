# app/models/store.py
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey, Decimal, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class StoreCategory(str, enum.Enum):
    RESTAURANT = "RESTAURANT"
    CAFE = "CAFE"
    SALON = "SALON"
    NAILSHOP = "NAILSHOP"
    CONVENIENCE_STORE = "CONVENIENCE_STORE"
    OTHER = "OTHER"


class StoreManagerRole(str, enum.Enum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    CASHIER = "CASHIER"


class Store(BaseModel):
    __tablename__ = "stores"

    name = Column(String(255), nullable=False)
    category = Column(Enum(StoreCategory), default=StoreCategory.OTHER)
    business_registration_number = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    managers = relationship("StoreManager", back_populates="store")
    location = relationship("StoreLocation", back_populates="store", uselist=False)
    contacts = relationship("StoreContact", back_populates="store")
    wallets = relationship("Wallet", back_populates="store")
    qr_codes = relationship("QRCode", back_populates="store")
    bonus_policies = relationship("BonusPolicy", back_populates="store")


class StoreManager(BaseModel):
    __tablename__ = "store_managers"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(StoreManagerRole), default=StoreManagerRole.MANAGER)
    is_active = Column(Boolean, default=True)

    # Relationships
    store = relationship("Store", back_populates="managers")
    user = relationship("User", back_populates="store_managements")

    __table_args__ = (
        {"schema": None},  # Ensures unique constraint
    )


class StoreLocation(BaseModel):
    __tablename__ = "store_locations"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, unique=True)
    address = Column(String, nullable=False)
    latitude = Column(Decimal(10, 8))
    longitude = Column(Decimal(11, 8))
    region = Column(String(100))
    postal_code = Column(String(20))

    # Relationships
    store = relationship("Store", back_populates="location")


class StoreContact(BaseModel):
    __tablename__ = "store_contacts"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    contact_type = Column(String(20), default="PHONE")
    contact_value = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)

    # Relationships
    store = relationship("Store", back_populates="contacts")
