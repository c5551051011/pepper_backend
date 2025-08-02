# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.user import UserResponse, UserCreate
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()
auth_service = AuthService()
user_service = UserService()

@router.patch("/profile", response_model=UserResponse, summary="Update user profile")
async def update_profile(
    user_update: dict,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information"""
    try:
        updated_user = user_service.update_user(db, current_user.id, user_update)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
