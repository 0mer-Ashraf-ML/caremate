# backend/api/endpoints/documents.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from backend.models.document import DocumentGenerationRequest
from backend.services.document_generation_service import DocumentGenerationService
from backend.services.coordinator_service import CoordinatorService

router = APIRouter()

# Dependency for document generation service
def get_doc_gen_service():
    return DocumentGenerationService()

@router.post("/generate")
async def generate_document(
    request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks,
    service: DocumentGenerationService = Depends(get_doc_gen_service)
):
    """Generate NDIS DOCX document"""
    try:
        # Resolve template_type
        template_type = request.template_type
        if not template_type and request.template_id:
            # Look up in DB using TemplateService
            template = service.template_service.get_template_by_id(request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            template_type = template["template_type"]

        if not template_type:
            raise HTTPException(status_code=400, detail="Must provide template_id or template_type")
        # Get coordinator info
        coordinator_service = CoordinatorService()
        coordinator = coordinator_service.get_coordinator_by_id(request.client_id)  # <-- adjust if different ID
        if not coordinator:
            raise HTTPException(status_code=404, detail="Coordinator not found")
        
        # Generate document
        result = service.generate_docx_document(
            client_id=request.client_id,
            template_type=request.template_id,   # careful: might need mapping ID->type
            context=request.context_description,
            coordinator_data={
                "coordinator_name": coordinator.coordinator_name,
                "provider_name": coordinator.provider_name,
                "email": coordinator.email,
                "phone": coordinator.phone
            }
        )
        
        return {
            "status": "success",
            "document_name": result["document_name"],
            "output_path": result["output_path"],
            "generated_at": result["generated_at"],
            "client_name": result["client_name"],
            "template_type": result["template_type"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{document_id}/edit")
async def edit_document(
    document_id: int,
    edit_request: str,
    service: DocumentGenerationService = Depends(get_doc_gen_service)
):
    """Edit document with AI assistance (future extension)"""
    try:
        # TODO: Load document from DB/output
        current_content = "Existing document content (to be implemented)"
        
        # For now, just return stub
        return {
            "document_id": document_id,
            "new_content": f"Edited with request: {edit_request}",
            "version": 2
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
