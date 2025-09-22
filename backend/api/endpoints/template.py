# backend/api/endpoints/templates.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from backend.services.template_service import TemplateService
from backend.models.document import DocumentTemplate

router = APIRouter()

def get_template_service() -> TemplateService:
    """Dependency to get template service"""
    return TemplateService()

@router.get("/", response_model=List[DocumentTemplate])
async def get_all_templates(
    active_only: bool = True,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get all NDIS document templates"""
    try:
        templates = template_service.get_all_ndis_templates(active_only=active_only)
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}"
        )

@router.get("/category/{category}")
async def get_templates_by_category(
    category: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get templates by category (e.g., 'assessment', 'progress_report')"""
    try:
        templates = template_service.get_templates_by_category(category)
        
        if not templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No templates found for category: {category}"
            )
        
        return {"category": category, "templates": templates}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{template_id}")
async def get_template_details(
    template_id: int,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get specific template details"""
    template = template_service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template

@router.get("/{template_id}/content")
async def get_template_content(
    template_id: int,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get template markdown content"""
    try:
        template = template_service.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Get template content
        content = template_service.get_template_content(template['template_path'])
        
        return {
            "template_id": template_id,
            "template_name": template['name'],
            "template_type": template['template_type'],
            "content": content,
            "fields_config": template.get('fields_config', {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template content: {str(e)}"
        )

@router.get("/types/available")
async def get_available_template_types():
    """Get list of available NDIS template types"""
    template_types = [
        {
            "type": "change_of_circumstance",
            "name": "Change of Circumstance",
            "description": "Document changes in participant circumstances requiring plan review",
            "icon": "🔄",
            "use_cases": ["Health condition changes", "Support needs evolution", "Living situation changes"]
        },
        {
            "type": "implementation_report", 
            "name": "Implementation Report",
            "description": "Report on NDIS plan implementation progress and outcomes",
            "icon": "📊",
            "use_cases": ["Plan progress review", "Service delivery updates", "Goal achievement tracking"]
        },
        {
            "type": "progress_report",
            "name": "Progress Report",
            "description": "Regular progress report on participant goals and support outcomes", 
            "icon": "📈",
            "use_cases": ["Quarterly reviews", "Goal progress tracking", "Support effectiveness"]
        },
        {
            "type": "support_plan",
            "name": "Support Plan",
            "description": "Comprehensive support plan outlining services and strategies",
            "icon": "🎯",
            "use_cases": ["New participant onboarding", "Support strategy updates", "Service coordination"]
        },
        {
            "type": "assessment",
            "name": "Assessment",
            "description": "Formal assessment of participant needs and capacity",
            "icon": "🔍", 
            "use_cases": ["Initial assessments", "Capacity evaluations", "Support needs analysis"]
        }
    ]
    
    return {"available_types": template_types, "total_count": len(template_types)}

@router.post("/preview")
async def preview_template_with_data(
    template_id: int,
    client_data: Dict[str, Any],
    coordinator_data: Dict[str, Any],
    context: str = "",
    template_service: TemplateService = Depends(get_template_service)
):
    """Preview template populated with provided data"""
    try:
        template = template_service.get_template_by_id(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Get template content
        template_content = template_service.get_template_content(template['template_path'])
        
        # Create preview data
        from datetime import datetime
        from jinja2 import Template
        
        template_vars = {
            'current_date': datetime.now().strftime('%d/%m/%Y'),
            'participant_name': client_data.get('full_name', 'Sample Participant'),
            'ndis_number': client_data.get('ndis_number', '123456789'),
            'coordinator_name': coordinator_data.get('coordinator_name', 'Sample Coordinator'),
            'provider_name': coordinator_data.get('provider_name', 'Sample Provider'),
            'context_description': context or 'Sample context for preview',
            **client_data,
            **coordinator_data
        }
        
        # Render template
        jinja_template = Template(template_content)
        preview_content = jinja_template.render(**template_vars)
        
        return {
            "template_id": template_id,
            "template_name": template['name'],
            "preview_content": preview_content,
            "populated_fields": list(template_vars.keys())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )