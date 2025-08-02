# app/repositories/wallet_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from uuid import UUID
from .base import BaseRepository
from app.models.wallet import Wallet, Transaction
from app.models.user import User


class WalletRepository(BaseRepository[Wallet]):
    def __init__(self):
        super().__init__(Wallet)

    def get_user_wallets(self, db: Session, user_id: UUID) -> List[Wallet]:
        """Get all wallets owned by a user with store info"""
        return db.query(Wallet).options(
            joinedload(Wallet.store),
            joinedload(Wallet.summary)
        ).filter(Wallet.owner_id == user_id).all()

    def get_store_wallets(self, db: Session, store_id: UUID, skip: int = 0, limit: int = 100) -> List[Wallet]:
        """Get all wallets for a store"""
        return db.query(Wallet).options(
            joinedload(Wallet.owner)
        ).filter(
            and_(Wallet.store_id == store_id, Wallet.status == "ACTIVE")
        ).offset(skip).limit(limit).all()

    def get_user_store_wallet(self, db: Session, user_id: UUID, store_id: UUID) -> Optional[Wallet]:
        """Get specific wallet for user at store"""
        return db.query(Wallet).filter(
            and_(Wallet.owner_id == user_id, Wallet.store_id == store_id)
        ).first()


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def get_wallet_transactions(
            self,
            db: Session,
            wallet_id: UUID,
            skip: int = 0,
            limit: int = 50
    ) -> List[Transaction]:
        """Get transactions for a wallet, ordered by most recent"""
        return db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id
        ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
