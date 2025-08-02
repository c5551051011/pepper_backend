# app/services/wallet_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID
from app.repositories.wallet_repository import WalletRepository, TransactionRepository
from app.models.wallet import Wallet, Transaction, WalletStatus, TransactionType, TransactionMethod
from app.core.exceptions import InsufficientFundsError, WalletNotFoundError


class WalletService:
    def __init__(self):
        self.wallet_repo = WalletRepository()
        self.transaction_repo = TransactionRepository()

    def create_wallet(self, db: Session, user_id: UUID, store_id: UUID, nickname: Optional[str] = None) -> Wallet:
        """Create a new wallet for user at store"""
        # Check if wallet already exists
        existing = self.wallet_repo.get_user_store_wallet(db, user_id, store_id)
        if existing:
            return existing

        wallet_data = {
            "owner_id": user_id,
            "store_id": store_id,
            "nickname": nickname,
            "balance": Decimal("0.00"),
            "bonus_balance": Decimal("0.00"),
            "status": WalletStatus.ACTIVE
        }
        return self.wallet_repo.create(db, obj_in=wallet_data)

    def charge_wallet(
            self,
            db: Session,
            wallet_id: UUID,
            amount: Decimal,
            method: TransactionMethod,
            created_by: UUID,
            description: Optional[str] = None
    ) -> Transaction:
        """Charge money to wallet with bonus calculation"""
        wallet = self.wallet_repo.get(db, wallet_id)
        if not wallet or wallet.status != WalletStatus.ACTIVE:
            raise WalletNotFoundError("Wallet not found or inactive")

        # Calculate bonus (5% default)
        bonus_amount = amount * Decimal("0.05")
        new_balance = wallet.balance + amount
        new_bonus_balance = wallet.bonus_balance + bonus_amount

        # Update wallet
        self.wallet_repo.update(db, db_obj=wallet, obj_in={
            "balance": new_balance,
            "bonus_balance": new_bonus_balance
        })

        # Create main transaction
        transaction_data = {
            "type": TransactionType.CHARGE,
            "method": method,
            "wallet_id": wallet_id,
            "amount": amount,
            "balance_after_transaction": new_balance + new_bonus_balance,
            "description": description,
            "created_by": created_by
        }
        transaction = self.transaction_repo.create(db, obj_in=transaction_data)

        # Create bonus transaction if bonus > 0
        if bonus_amount > 0:
            bonus_transaction_data = {
                "type": TransactionType.BONUS_EARNED,
                "method": method,
                "wallet_id": wallet_id,
                "amount": bonus_amount,
                "balance_after_transaction": new_balance + new_bonus_balance,
                "description": f"5% bonus for {amount} charge",
                "created_by": created_by,
                "reference_transaction_id": transaction.id
            }
            self.transaction_repo.create(db, obj_in=bonus_transaction_data)

        return transaction

    def spend_from_wallet(
            self,
            db: Session,
            wallet_id: UUID,
            amount: Decimal,
            method: TransactionMethod,
            created_by: UUID,
            description: Optional[str] = None
    ) -> Transaction:
        """Spend money from wallet (use bonus first, then regular balance)"""
        wallet = self.wallet_repo.get(db, wallet_id)
        if not wallet or wallet.status != WalletStatus.ACTIVE:
            raise WalletNotFoundError("Wallet not found or inactive")

        total_available = wallet.balance + wallet.bonus_balance
        if total_available < amount:
            raise InsufficientFundsError(f"Insufficient funds. Available: {total_available}, Required: {amount}")

        # Use bonus balance first
        remaining_amount = amount
        bonus_used = min(wallet.bonus_balance, remaining_amount)
        remaining_amount -= bonus_used
        regular_used = remaining_amount

        new_bonus_balance = wallet.bonus_balance - bonus_used
        new_balance = wallet.balance - regular_used

        # Update wallet
        self.wallet_repo.update(db, db_obj=wallet, obj_in={
            "balance": new_balance,
            "bonus_balance": new_bonus_balance
        })

        # Create transaction
        transaction_data = {
            "type": TransactionType.SPEND,
            "method": method,
            "wallet_id": wallet_id,
            "amount": amount,
            "balance_after_transaction": new_balance + new_bonus_balance,
            "description": description,
            "created_by": created_by
        }
        return self.transaction_repo.create(db, obj_in=transaction_data)

    def get_user_wallets(self, db: Session, user_id: UUID) -> List[Wallet]:
        """Get all wallets for a user"""
        return self.wallet_repo.get_user_wallets(db, user_id)

    def get_wallet_transactions(self, db: Session, wallet_id: UUID, skip: int = 0, limit: int = 50) -> List[
        Transaction]:
        """Get transaction history for a wallet"""
        return self.transaction_repo.get_wallet_transactions(db, wallet_id, skip, limit)
