# backend/api/endpoints/clients.py
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from backend.models.client import ClientFolder, ClientFolderCreate, ClientDocument
from backend.services.client_service import ClientService
from backend.services.extraction_service import ExtractionService

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=ClientFolder)
async def create_client(
    client: ClientFolderCreate,
    service: ClientService = Depends()
):
    """Create new client folder"""
    try:
        return service.create_client_folder(client)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/coordinator/{coordinator_id}", response_model=List[ClientFolder])
async def get_coordinator_clients(
    coordinator_id: int,
    service: ClientService = Depends()
):
    """Get all clients for coordinator"""
    return service.get_coordinator_clients(coordinator_id)


@router.get("/{client_id}", response_model=ClientFolder)
async def get_client(
    client_id: int,
    service: ClientService = Depends()
):
    """Get client by ID"""
    client = service.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/{client_id}/documents", response_model=List[ClientDocument])
async def get_client_documents(
    client_id: int,
    service: ClientService = Depends()
):
    """Get all documents for client"""
    return service.get_client_documents(client_id)


@router.post("/{client_id}/documents")
async def upload_client_document(
    client_id: int,
    document_name: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    service: ClientService = Depends(),
    extractor: ExtractionService = Depends()
):
    """
    Upload document → save file → store raw text into DB.
    """
    try:
        # Save uploaded file to disk
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"client_{client_id}_{document_name}{file_ext}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Add record in client_documents
        doc_id = service.add_client_document(
            client_id, document_name, document_type, file_path
        )

        # Store raw text in client_extracted_data
        extractor.store_raw_document(client_id, document_type, file_path)

        return {
            "document_id": doc_id,
            "message": "✅ Document uploaded and raw text stored successfully",
            "file_path": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
