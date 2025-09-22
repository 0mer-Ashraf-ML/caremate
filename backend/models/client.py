# backend/models/client.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

class ClientFolderBase(BaseModel):
    full_name: str
    ndis_number: str
    plan_start_date: Optional[date] = None
    plan_end_date: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    conditions: Optional[List[str]] = []
    coordinator_notes: Optional[str] = ""
    goals_advocacy: bool = False
    goals_support: bool = False
    goals_capacity_building: bool = False
    goals_funding_increase: bool = False
    goals_other: Optional[str] = ""

class ClientFolderCreate(ClientFolderBase):
    coordinator_id: int

class ClientFolder(ClientFolderBase):
    id: int
    coordinator_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ClientDocument(BaseModel):
    id: int
    client_id: int
    document_name: str
    document_type: str
    file_path: str
    extracted_content: Optional[str] = ""
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
