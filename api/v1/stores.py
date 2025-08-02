# app/api/v1/stores.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.database import get_db
from app.schemas.store import StoreCreate, StoreResponse
from app.services.auth_service import AuthService
from app.services.store_service import StoreService
from app.models.user import User

router = APIRouter()
auth_service = AuthService()
store_service = StoreService()


@router.post("/", response_model=StoreResponse, summary="Create new store")
async def create_store(
        store_data: StoreCreate,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Create a new store (user becomes owner/manager)"""
    try:
        store = store_service.create_store(db, store_data, current_user.id)
        return store
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nearby", response_model=List[StoreResponse], summary="Find nearby stores")
async def get_nearby_stores(
        latitude: Decimal = Query(..., description="User's latitude"),
        longitude: Decimal = Query(..., description="User's longitude"),
        radius_km: int = Query(5, description="Search radius in kilometers"),
        category: Optional[str] = Query(None, description="Store category filter"),
        db: Session = Depends(get_db)
):
    """Find stores near user's location"""
    try:
        stores = store_service.find_nearby_stores(db, latitude, longitude, radius_km, category)
        return stores
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/managed", response_model=List[StoreResponse], summary="Get stores managed by current user")
async def get_managed_stores(
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Get all stores managed by current user"""
    try:
        stores = store_service.get_user_managed_stores(db, current_user.id)
        return stores
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{store_id}", response_model=StoreResponse, summary="Get store details")
async def get_store(
        store_id: str,
        db: Session = Depends(get_db)
):
    """Get store information by ID"""
    try:
        store = store_service.get_store(db, store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return store
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{store_id}/qr", summary="Get store QR code")
async def get_store_qr_code(
        store_id: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Get QR code for store payments (store managers only)"""
    try:
        # Verify user manages this store
        if not store_service.user_manages_store(db, current_user.id, store_id):
            raise HTTPException(status_code=403, detail="Access denied")

        qr_code = store_service.get_or_create_qr_code(db, store_id)
        return {"qr_code": qr_code.qr_code_data, "store_id": store_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
