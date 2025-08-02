# app/api/v1/transactions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.schemas.wallet import TransactionCreate, TransactionResponse
from app.services.auth_service import AuthService
from app.services.wallet_service import WalletService
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.wallet import TransactionMethod
from app.core.exceptions import WalletNotFoundError, InsufficientFundsError

router = APIRouter()
auth_service = AuthService()
wallet_service = WalletService()
notification_service = NotificationService()


@router.post("/charge", response_model=TransactionResponse, summary="Charge wallet")
async def charge_wallet(
        wallet_id: UUID,
        transaction_data: TransactionCreate,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Charge money to wallet (store managers only)"""
    try:
        # Verify transaction type
        if transaction_data.type != "CHARGE":
            raise HTTPException(status_code=400, detail="Invalid transaction type for charge endpoint")

        # Verify user can charge this wallet (store manager)
        if not wallet_service.can_user_manage_wallet(db, current_user.id, wallet_id):
            raise HTTPException(status_code=403, detail="Access denied")

        transaction = wallet_service.charge_wallet(
            db,
            wallet_id,
            transaction_data.amount,
            TransactionMethod(transaction_data.method),
            current_user.id,
            transaction_data.description
        )

        # Send notifications (async)
        await notification_service.send_transaction_notifications(db, transaction)

        return transaction

    except WalletNotFoundError:
        raise HTTPException(status_code=404, detail="Wallet not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/spend", response_model=TransactionResponse, summary="Spend from wallet")
async def spend_from_wallet(
        wallet_id: UUID,
        transaction_data: TransactionCreate,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Spend money from wallet (wallet owner or store manager)"""
    try:
        # Verify transaction type
        if transaction_data.type != "SPEND":
            raise HTTPException(status_code=400, detail="Invalid transaction type for spend endpoint")

        # Verify user can spend from this wallet
        if not wallet_service.can_user_spend_from_wallet(db, current_user.id, wallet_id):
            raise HTTPException(status_code=403, detail="Access denied")

        transaction = wallet_service.spend_from_wallet(
            db,
            wallet_id,
            transaction_data.amount,
            TransactionMethod(transaction_data.method),
            current_user.id,
            transaction_data.description
        )

        # Send notifications (async)
        await notification_service.send_transaction_notifications(db, transaction)

        return transaction

    except WalletNotFoundError:
        raise HTTPException(status_code=404, detail="Wallet not found")
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/qr-payment", summary="Process QR code payment")
async def process_qr_payment(
        qr_code: str,
        amount: float,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Process payment using store QR code"""
    try:
        result = wallet_service.process_qr_payment(db, qr_code, amount, current_user.id)
        return result
    except WalletNotFoundError:
        raise HTTPException(status_code=404, detail="Wallet or store not found")
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
