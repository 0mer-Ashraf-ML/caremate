# backend/api/endpoints/forms.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from backend.models.document import DocumentGenerationRequest, GeneratedDocument
from backend.services.document_service import DocumentService
from backend.services.client_service import ClientService
from backend.services.coordinator_service import CoordinatorService
from backend.services.document_service import DocumentService
from config.database import DatabaseManager

router = APIRouter()

def get_document_generation_service() -> DocumentService:
    """Dependency to get document generation service"""
    return DocumentService()

def get_client_service() -> ClientService:
    """Dependency to get client service"""
    return ClientService()

def get_coordinator_service() -> CoordinatorService:
    """Dependency to get coordinator service"""
    return CoordinatorService()

@router.post("/generate")
async def generate_ndis_document(
    request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks,
    doc_service: DocumentService = Depends(get_document_generation_service),
    coord_service: CoordinatorService = Depends(get_coordinator_service)
):
    """Generate NDIS document from template and client data"""
    try:
        # Get client data
        client = doc_service.client_service.get_client_by_id(request.client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Get coordinator data (assuming coordinator_id = 1 for MVP)
        coordinator = coord_service.get_coordinator_by_id(1)
        if not coordinator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coordinator not found"
            )
        
        # Check credits
        credits_required = 10  # 10 credits per generation
        if coordinator.credits_balance < credits_required:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {credits_required}, Available: {coordinator.credits_balance}"
            )
        
        # Generate document
        result = await doc_service.generate_complete_document(
            client_id=request.client_id,
            template_type=request.template_type,
            context=request.context_description,
            coordinator_data=coordinator.__dict__,
            supporting_docs=request.support_documents or []
        )
        
        # Deduct credits
        coord_service.update_credits(1, -credits_required)
        
        # Save to database
        db = DatabaseManager()
        doc_id = db.execute_insert("""
            INSERT INTO generated_documents 
            (coordinator_id, client_id, template_id, document_name, content, credits_used, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # coordinator_id
            request.client_id,
            request.template_id,
            result['document_name'],
            result['content'],
            credits_required,
            'draft'
        ))
        
        return {
            "document_id": doc_id,
            "document_name": result['document_name'],
            "template_type": result['template_type'],
            "client_name": result['client_name'],
            "content": result['content'],
            "credits_used": credits_required,
            "status": "generated",
            "generated_at": result['generated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation failed: {str(e)}"
        )

@router.put("/{document_id}/edit")
async def edit_document_with_ai(
    document_id: int,
    edit_request: str,
    coordinator_id: int = 1,
    doc_service: DocumentService = Depends(get_document_generation_service),
    coord_service: CoordinatorService = Depends(get_coordinator_service)
):
    """Edit document using AI assistance"""
    try:
        # Check credits
        credits_required = 5  # 5 credits per edit
        coordinator = coord_service.get_coordinator_by_id(coordinator_id)
        
        if coordinator.credits_balance < credits_required:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits for editing. Required: {credits_required}"
            )
        
        # Get current document
        db = DatabaseManager()
        doc_query = "SELECT * FROM generated_documents WHERE id = ?"
        doc_result = db.execute_query(doc_query, (document_id,))
        
        if not doc_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        current_doc = dict(doc_result[0])
        current_content = current_doc['content']
        
        # Generate AI edit suggestions
        edited_content = await doc_service.ai_service.suggest_document_edits(
            current_content, edit_request
        )
        
        # Update document
        new_version = current_doc['version'] + 1
        
        update_query = """
            UPDATE generated_documents 
            SET content = ?, version = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        db.execute_query(update_query, (edited_content, new_version, document_id))
        
        # Save version history
        version_query = """
            INSERT INTO document_versions (document_id, version_number, content, changes_description)
            VALUES (?, ?, ?, ?)
        """
        db.execute_insert(version_query, (
            document_id, new_version, edited_content, edit_request
        ))
        
        # Deduct credits
        coord_service.update_credits(coordinator_id, -credits_required)
        
        return {
            "document_id": document_id,
            "new_version": new_version,
            "edited_content": edited_content,
            "edit_request": edit_request,
            "credits_used": credits_required,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document editing failed: {str(e)}"
        )

@router.get("/coordinator/{coordinator_id}/documents")
async def get_coordinator_documents(
    coordinator_id: int,
    limit: int = 20,
    status_filter: Optional[str] = None,
    template_type_filter: Optional[str] = None
):
    """Get all documents for a coordinator with optional filtering"""
    try:
        db = DatabaseManager()
        
        # Build query with filters
        base_query = """
            SELECT gd.*, cf.full_name as client_name, dt.name as template_name
            FROM generated_documents gd
            JOIN client_folders cf ON gd.client_id = cf.id
            JOIN document_templates dt ON gd.template_id = dt.id
            WHERE gd.coordinator_id = ?
        """
        
        params = [coordinator_id]
        
        if status_filter:
            base_query += " AND gd.status = ?"
            params.append(status_filter)
        
        if template_type_filter:
            base_query += " AND dt.template_type = ?"
            params.append(template_type_filter)
        
        base_query += " ORDER BY gd.created_at DESC LIMIT ?"
        params.append(limit)
        
        results = db.execute_query(base_query, tuple(params))
        
        documents = []
        for row in results:
            doc_dict = dict(row)
            documents.append(doc_dict)
        
        return {
            "coordinator_id": coordinator_id,
            "total_documents": len(documents),
            "documents": documents,
            "filters_applied": {
                "status": status_filter,
                "template_type": template_type_filter,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )

@router.get("/{document_id}")
async def get_document_details(
    document_id: int
):
    """Get specific document details"""
    try:
        db = DatabaseManager()
        
        query = """
            SELECT gd.*, cf.full_name as client_name, dt.name as template_name
            FROM generated_documents gd
            JOIN client_folders cf ON gd.client_id = cf.id  
            JOIN document_templates dt ON gd.template_id = dt.id
            WHERE gd.id = ?
        """
        
        result = db.execute_query(query, (document_id,))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = dict(result[0])
        
        # Get version history
        version_query = """
            SELECT version_number, changes_description, created_at
            FROM document_versions 
            WHERE document_id = ?
            ORDER BY version_number DESC
        """
        versions = db.execute_query(version_query, (document_id,))
        
        document['version_history'] = [dict(v) for v in versions]
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )

@router.post("/{document_id}/export")
async def export_document(
    document_id: int,
    output_format: str = "pdf",
    doc_service: DocumentService = Depends(get_document_generation_service)
):
    """Export document to PDF or DOCX format"""
    try:
        # Get document content
        db = DatabaseManager()
        doc_query = "SELECT * FROM generated_documents WHERE id = ?"
        doc_result = db.execute_query(doc_query, (document_id,))
        
        if not doc_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        document = dict(doc_result[0])
        
        # Generate file
        output_path = await doc_service.doc_service.generate_professional_document(
            content=document['content'],
            template_name=document['document_name'],
            output_format=output_format
        )
        
        # Update document with output path
        update_query = "UPDATE generated_documents SET output_path = ? WHERE id = ?"
        db.execute_query(update_query, (output_path, document_id))
        
        return {
            "document_id": document_id,
            "output_format": output_format,
            "file_path": output_path,
            "download_url": f"/api/forms/download/{document_id}",
            "exported_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )

@router.get("/download/{document_id}")
async def download_document(document_id: int):
    """Download generated document file"""
    try:
        db = DatabaseManager()
        query = "SELECT output_path, document_name FROM generated_documents WHERE id = ?"
        result = db.execute_query(query, (document_id,))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = dict(result[0])
        file_path = doc_data['output_path']
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found"
            )
        
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    coordinator_id: int = 1
):
    """Delete a generated document"""
    try:
        db = DatabaseManager()
        
        # Verify document belongs to coordinator
        verify_query = """
            SELECT output_path FROM generated_documents 
            WHERE id = ? AND coordinator_id = ?
        """
        result = db.execute_query(verify_query, (document_id, coordinator_id))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        
        # Delete file if exists
        file_path = result[0]['output_path']
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        delete_query = "DELETE FROM generated_documents WHERE id = ?"
        db.execute_query(delete_query, (document_id,))
        
        # Delete version history
        version_delete_query = "DELETE FROM document_versions WHERE document_id = ?"
        db.execute_query(version_delete_query, (document_id,))
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.post("/upload-support-document")
async def upload_support_document(
    client_id: int,
    file: UploadFile = File(...),
    document_type: str = "other",
    client_service: ClientService = Depends(get_client_service)
):
    """Upload supporting document for client"""
    try:
        # Validate file type
        allowed_extensions = ['pdf', 'docx', 'txt']
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        upload_dir = "./uploads/client_documents"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"client_{client_id}_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Write file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract content using document service
        doc_service = DocumentService()
        extracted_content = await doc_service.extract_document_content(file_path)
        
        # Save to database
        doc_id = client_service.add_client_document(
            client_id=client_id,
            document_name=file.filename,
            document_type=document_type,
            file_path=file_path,
            content=extracted_content[:2000]  # Store first 2000 chars
        )
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "document_type": document_type,
            "file_path": file_path,
            "extracted_content_length": len(extracted_content),
            "uploaded_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/client/{client_id}/documents")
async def get_client_support_documents(
    client_id: int,
    client_service: ClientService = Depends(get_client_service)
):
    """Get all support documents for a client"""
    try:
        documents = client_service.get_client_documents(client_id)
        
        return {
            "client_id": client_id,
            "total_documents": len(documents),
            "documents": [doc.__dict__ for doc in documents]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve client documents: {str(e)}"
        )

@router.post("/analyze-context")
async def analyze_document_context(
    template_type: str,
    context_description: str,
    client_data: Dict[str, Any],
    doc_service: DocumentService = Depends(get_document_generation_service)
):
    """Analyze context and provide generation suggestions"""
    try:
        # Use AI to analyze context and provide suggestions
        suggestions = await doc_service.ai_service.analyze_context_for_template(
            template_type, context_description, client_data
        )
        
        return {
            "template_type": template_type,
            "context_analysis": suggestions,
            "suggestions": [
                "Include specific dates and timeframes",
                "Reference supporting documentation",
                "Focus on measurable outcomes",
                "Use person-centered language"
            ],
            "estimated_credits": 10
        }
        
    except Exception as e:
        return {
            "template_type": template_type,
            "context_analysis": "Context analysis unavailable",
            "suggestions": [
                "Provide clear, specific context",
                "Include relevant supporting information",
                "Focus on participant outcomes"
            ],
            "estimated_credits": 10
        }

@router.get("/stats/generation")
async def get_generation_statistics():
    """Get overall document generation statistics"""
    try:
        db = DatabaseManager()
        
        # Total documents
        total_query = "SELECT COUNT(*) FROM generated_documents"
        total_result = db.execute_query(total_query)
        total_docs = total_result[0][0] if total_result else 0
        
        # Documents by template type
        type_query = """
            SELECT dt.template_type, COUNT(*) as count
            FROM generated_documents gd
            JOIN document_templates dt ON gd.template_id = dt.id
            GROUP BY dt.template_type
        """
        type_results = db.execute_query(type_query)
        
        # Documents by status
        status_query = """
            SELECT status, COUNT(*) as count
            FROM generated_documents
            GROUP BY status
        """
        status_results = db.execute_query(status_query)
        
        return {
            "total_documents": total_docs,
            "by_template_type": {row[0]: row[1] for row in type_results},
            "by_status": {row[0]: row[1] for row in status_results},
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )