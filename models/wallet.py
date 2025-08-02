# app/models/wallet.py
from sqlalchemy import Column, String, Boolean, Decimal, ForeignKey, Enum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class WalletStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class WalletMemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class TransactionType(str, enum.Enum):
    CHARGE = "CHARGE"
    SPEND = "SPEND"
    BONUS_EARNED = "BONUS_EARNED"
    CREDIT_TRANSFER = "CREDIT_TRANSFER"
    CREDIT_SALE = "CREDIT_SALE"
    REFUND = "REFUND"


class TransactionMethod(str, enum.Enum):
    CARD = "CARD"
    CASH = "CASH"
    EXTERNAL_APP = "EXTERNAL_APP"
    TRANSFER = "TRANSFER"


class Wallet(BaseModel):
    __tablename__ = "wallets"

    nickname = Column(String(100))
    status = Column(Enum(WalletStatus), default=WalletStatus.ACTIVE, index=True)
    balance = Column(Decimal(12, 2), default=0.00, nullable=False)
    bonus_balance = Column(Decimal(12, 2), default=0.00, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, index=True)
    is_shared = Column(Boolean, default=False, index=True)

    # Relationships
    owner = relationship("User", back_populates="owned_wallets")
    store = relationship("Store", back_populates="wallets")
    members = relationship("WalletMember", back_populates="wallet", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="wallet")
    summary = relationship("WalletSummary", back_populates="wallet", uselist=False)

    __table_args__ = (
        {"schema": None},  # For unique constraint on owner_id, store_id
    )


class WalletMember(BaseModel):
    __tablename__ = "wallet_members"

    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(WalletMemberRole), default=WalletMemberRole.MEMBER)

    # Relationships
    wallet = relationship("Wallet", back_populates="members")
    user = relationship("User", back_populates="wallet_memberships")


class WalletSummary(BaseModel):
    __tablename__ = "wallet_summaries"

    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, unique=True)
    total_charge_amount = Column(Decimal(12, 2), default=0.00)
    total_spend_amount = Column(Decimal(12, 2), default=0.00)
    total_bonus_earned = Column(Decimal(12, 2), default=0.00)
    transaction_count = Column(Integer, default=0)

    # Relationships
    wallet = relationship("Wallet", back_populates="summary")


class Transaction(BaseModel):
    __tablename__ = "transactions"

    type = Column(Enum(TransactionType), nullable=False, index=True)
    method = Column(Enum(TransactionMethod), nullable=False)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True)
    amount = Column(Decimal(12, 2), nullable=False)
    fee_amount = Column(Decimal(12, 2), default=0.00)
    balance_after_transaction = Column(Decimal(12, 2), nullable=False)
    description = Column(Text)
    reference_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_transactions")
    reference_transaction = relationship("Transaction", remote_side="Transaction.id")


class BonusPolicy(BaseModel):
    __tablename__ = "bonus_policies"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    bonus_rate = Column(Decimal(5, 4), default=0.05)  # 5%
    minimum_charge_amount = Column(Decimal(12, 2), default=0)
    maximum_bonus_amount = Column(Decimal(12, 2))
    is_active = Column(Boolean, default=True)

    # Relationships
    store = relationship("Store", back_populates="bonus_policies")


class QRCode(BaseModel):
    __tablename__ = "qr_codes"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    qr_code_data = Column(String(500), nullable=False, unique=True)
    qr_type = Column(String(20), default="PAYMENT")
    is_active = Column(Boolean, default=True)

    # Relationships
    store = relationship("Store", back_populates="qr_codes")
