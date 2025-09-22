# backend/models/document.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class DocumentTemplate(BaseModel):
    id: int
    name: str
    template_type: str
    template_path: str
    description: Optional[str] = ""
    fields_config: Dict[str, Any]
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentGenerationRequest(BaseModel):
    client_id: int
    template_id: Optional[int] = None   # Accept either ID...
    template_type: Optional[str] = None # ...or direct type string
    context_description: str
    support_documents: Optional[List[str]] = []  # File paths

class GeneratedDocument(BaseModel):
    id: int
    coordinator_id: int
    client_id: int
    template_id: int
    template_type: str   # NEW field
    document_name: str
    content: str
    output_path: Optional[str] = ""
    version: int = 1
    credits_used: int = 0
    status: str = "draft"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True