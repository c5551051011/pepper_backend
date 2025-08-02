# app/services/auth_service.py
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import random
import asyncio

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.exceptions import InvalidVerificationCodeError, UserNotVerifiedError

security = HTTPBearer()


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    async def send_verification_code(self, db: Session, phone_number: str) -> dict:
        """Send SMS verification code"""
        # Generate 6-digit code
        code = f"{random.randint(100000, 999999)}"

        # Save verification code to database
        verification_data = {
            "phone_number": phone_number,
            "verification_code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "is_verified": False,
            "attempts_count": 0
        }

        # TODO: Integrate with SMS service (KakaoTalk SMS, Naver Cloud Platform SMS, etc.)
        # For now, just log the code (remove in production!)
        print(f"SMS Verification Code for {phone_number}: {code}")

        # In production, send actual SMS here
        # await self.sms_service.send_sms(phone_number, f"StoreCredit 인증번호: {code}")

        return {"status": "sent", "expires_in": 600}

    def verify_phone_and_get_user(self, db: Session, phone_number: str, code: str) -> User:
        """Verify phone number and return/create user"""
        # TODO: Verify code from database
        # For MVP, accept any 6-digit code
        if len(code) != 6 or not code.isdigit():
            raise InvalidVerificationCodeError("Invalid verification code format")

        # Get or create user
        user = self.user_repo.get_by_phone(db, phone_number)
        if not user:
            # Create new user
            user_data = {
                "phone_number": phone_number,
                "name": f"User {phone_number[-4:]}",  # Default name
                "is_verified": True
            }
            user = self.user_repo.create(db, obj_in=user_data)
        else:
            # Update verification status
            self.user_repo.update(db, db_obj=user, obj_in={"is_verified": True})

        return user

    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def get_current_user(
            self,
            credentials: HTTPAuthorizationCredentials = Depends(security),
            db: Session = Depends(get_db)
    ) -> User:
        """Get current authenticated user"""
        try:
            payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = self.user_repo.get(db, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        if not user.is_verified:
            raise HTTPException(status_code=401, detail="Phone not verified")

        return user