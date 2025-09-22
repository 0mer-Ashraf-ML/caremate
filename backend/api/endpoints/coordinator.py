# backend/api/endpoints/coordinator.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from backend.models.coordinator import CoordinatorProfile, CoordinatorProfileCreate
from backend.services.coordinator_service import CoordinatorService

router = APIRouter()

@router.post("/", response_model=CoordinatorProfile)
async def create_coordinator(
    profile: CoordinatorProfileCreate,
    service: CoordinatorService = Depends()
):
    """Create coordinator profile"""
    try:
        return service.create_coordinator_profile(profile)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{coordinator_id}", response_model=CoordinatorProfile)
async def get_coordinator(
    coordinator_id: int,
    service: CoordinatorService = Depends()
):
    """Get coordinator by ID"""
    coordinator = service.get_coordinator_by_id(coordinator_id)
    if not coordinator:
        raise HTTPException(status_code=404, detail="Coordinator not found")
    return coordinator

@router.put("/{coordinator_id}/credits")
async def update_credits(
    coordinator_id: int,
    credit_change: int,
    service: CoordinatorService = Depends()
):
    """Update coordinator credits"""
    success = service.update_credits(coordinator_id, credit_change)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update credits")
    
    return {"message": "Credits updated successfully"}

@router.get("/{coordinator_id}/credits")
async def get_credits_balance(
    coordinator_id: int,
    service: CoordinatorService = Depends()
):
    """Get coordinator credits balance"""
    balance = service.get_credits_balance(coordinator_id)
    return {"credits_balance": balance}
