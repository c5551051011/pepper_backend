# app/api/v1/wallets.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.wallet import WalletCreate, WalletResponse, TransactionCreate, TransactionResponse
from app.services.auth_service import AuthService
from app.services.wallet_service import WalletService
from app.models.user import User
from app.core.exceptions import WalletNotFoundError, InsufficientFundsError

router = APIRouter()
auth_service = AuthService()
wallet_service = WalletService()

@router.get("/", response_model=List[WalletResponse], summary="Get user's wallets")
async def get_my_wallets(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wallets owned by current user"""
    try:
        wallets = wallet_service.get_user_wallets(db, current_user.id)
        return wallets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=WalletResponse, summary="Create wallet at store")
async def create_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wallet for current user at specified store"""
    try:
        wallet = wallet_service.create_wallet(
            db,
            current_user.id,
            wallet_data.store_id,
            wallet_data.nickname
        )
        return wallet
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{wallet_id}", response_model=WalletResponse, summary="Get wallet details")
async def get_wallet(
    wallet_id: UUID,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get wallet details (owner or store manager only)"""
    try:
        wallet = wallet_service.get_wallet_with_access_check(db, wallet_id, current_user.id)
        return wallet
    except WalletNotFoundError:
        raise HTTPException(status_code=404, detail="Wallet not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{wallet_id}/transactions", response_model=List[TransactionResponse], summary="Get wallet transactions")
async def get_wallet_transactions(
    wallet_id: UUID,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction history for wallet"""
    try:
        # Verify access
        wallet_service.get_wallet_with_access_check(db, wallet_id, current_user.id)
        transactions = wallet_service.get_wallet_transactions(db, wallet_id, skip, limit)
        return transactions
    except WalletNotFoundError:
        raise HTTPException(status_code=404, detail="Wallet not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
