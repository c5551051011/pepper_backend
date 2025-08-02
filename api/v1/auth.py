# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import jwt
import random

from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import InvalidVerificationCodeError, UserNotVerifiedError
from app.schemas.user import PhoneVerificationRequest, PhoneVerificationConfirm, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


@router.post("/send-verification", summary="Send SMS verification code")
async def send_verification_code(
        request: PhoneVerificationRequest,
        db: Session = Depends(get_db)
):
    """Send 6-digit verification code to phone number"""
    try:
        result = await auth_service.send_verification_code(db, request.phone_number)
        return {"message": "Verification code sent successfully", "expires_in": 600}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-phone", response_model=UserResponse, summary="Verify phone and create/login user")
async def verify_phone_and_login(
        request: PhoneVerificationConfirm,
        db: Session = Depends(get_db)
):
    """Verify phone number and return user with access token"""
    try:
        user = auth_service.verify_phone_and_get_user(db, request.phone_number, request.verification_code)
        access_token = auth_service.create_access_token(user.id)

        return {
            **UserResponse.from_orm(user).dict(),
            "access_token": access_token,
            "token_type": "bearer"
        }
    except InvalidVerificationCodeError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_current_user(
        current_user: User = Depends(auth_service.get_current_user)
):
    """Get current authenticated user information"""
    return current_user