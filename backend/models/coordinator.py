# backend/models/coordinator.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CoordinatorProfileBase(BaseModel):
    provider_name: str
    coordinator_name: str
    email: EmailStr
    phone: Optional[str] = None

class CoordinatorProfileCreate(CoordinatorProfileBase):
    pass

class CoordinatorProfile(CoordinatorProfileBase):
    id: int
    profile_complete: bool = False
    credits_balance: int = 100
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True