# backend/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import json
from backend.models.coordinator import CoordinatorProfile, CoordinatorProfileCreate
from backend.services.coordinator_service import CoordinatorService
from config.database import DatabaseManager

router = APIRouter()

def get_coordinator_service() -> CoordinatorService:
    """Dependency to get coordinator service"""
    return CoordinatorService()

@router.post("/coordinator", response_model=CoordinatorProfile)
async def create_coordinator_profile(
    profile: CoordinatorProfileCreate,
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Create new coordinator profile"""
    try:
        coordinator = service.create_coordinator_profile(profile)
        return coordinator
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create coordinator profile: {str(e)}"
        )

@router.get("/coordinator/{coordinator_id}", response_model=CoordinatorProfile)
async def get_coordinator_profile(
    coordinator_id: int,
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Get coordinator profile by ID"""
    coordinator = service.get_coordinator_by_id(coordinator_id)
    
    if not coordinator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coordinator profile not found"
        )
    
    return coordinator

@router.get("/coordinator/email/{email}", response_model=CoordinatorProfile)
async def get_coordinator_by_email(
    email: str,
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Get coordinator profile by email"""
    coordinator = service.get_coordinator_by_email(email)
    
    if not coordinator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coordinator not found with this email"
        )
    
    return coordinator

@router.put("/coordinator/{coordinator_id}")
async def update_coordinator_profile(
    coordinator_id: int,
    profile_updates: dict,
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Update coordinator profile"""
    try:
        # Get current profile
        coordinator = service.get_coordinator_by_id(coordinator_id)
        if not coordinator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coordinator not found"
            )
        
        # Update profile (simplified for MVP)
        db = DatabaseManager()
        
        update_fields = []
        params = []
        
        if 'provider_name' in profile_updates:
            update_fields.append("provider_name = ?")
            params.append(profile_updates['provider_name'])
        
        if 'coordinator_name' in profile_updates:
            update_fields.append("coordinator_name = ?")
            params.append(profile_updates['coordinator_name'])
        
        if 'email' in profile_updates:
            update_fields.append("email = ?")
            params.append(profile_updates['email'])
        
        if 'phone' in profile_updates:
            update_fields.append("phone = ?")
            params.append(profile_updates['phone'])
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(coordinator_id)
            
            query = f"UPDATE coordinator_profiles SET {', '.join(update_fields)} WHERE id = ?"
            db.execute_query(query, tuple(params))
        
        # Return updated profile
        updated_coordinator = service.get_coordinator_by_id(coordinator_id)
        return {"message": "Profile updated successfully", "coordinator": updated_coordinator}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/coordinator/{coordinator_id}/credits")
async def update_credits(
    coordinator_id: int,
    credit_change: int,
    operation: str = "add",  # "add" or "deduct"
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Update coordinator credits"""
    try:
        # Validate coordinator exists
        coordinator = service.get_coordinator_by_id(coordinator_id)
        if not coordinator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coordinator not found"
            )
        
        # Apply credit change
        if operation == "deduct":
            credit_change = -abs(credit_change)
        elif operation == "add":
            credit_change = abs(credit_change)
        
        success = service.update_credits(coordinator_id, credit_change)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update credits"
            )
        
        # Get updated balance
        new_balance = service.get_credits_balance(coordinator_id)
        
        return {
            "message": f"Credits {operation}ed successfully",
            "credit_change": credit_change,
            "new_balance": new_balance
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/coordinator/{coordinator_id}/credits")
async def get_credits_balance(
    coordinator_id: int,
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Get coordinator's current credit balance"""
    coordinator = service.get_coordinator_by_id(coordinator_id)
    
    if not coordinator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coordinator not found"
        )
    
    balance = service.get_credits_balance(coordinator_id)
    
    return {
        "coordinator_id": coordinator_id,
        "credits_balance": balance,
        "coordinator_name": coordinator.coordinator_name
    }

@router.get("/coordinator/{coordinator_id}/usage-stats")
async def get_usage_statistics(
    coordinator_id: int,
    service: CoordinatorService = Depends(get_coordinator_service)
):
    """Get coordinator's usage statistics"""
    coordinator = service.get_coordinator_by_id(coordinator_id)
    
    if not coordinator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coordinator not found"
        )
    
    # Get stats from database
    db = DatabaseManager()
    
    # Count clients
    client_count_query = "SELECT COUNT(*) FROM client_folders WHERE coordinator_id = ?"
    client_result = db.execute_query(client_count_query, (coordinator_id,))
    client_count = client_result[0][0] if client_result else 0
    
    # Count documents
    doc_count_query = "SELECT COUNT(*) FROM generated_documents WHERE coordinator_id = ?"
    doc_result = db.execute_query(doc_count_query, (coordinator_id,))
    doc_count = doc_result[0][0] if doc_result else 0
    
    return {
        "coordinator_id": coordinator_id,
        "total_clients": client_count,
        "total_documents": doc_count,
        "credits_remaining": coordinator.credits_balance
    }