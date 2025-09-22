# backend/api/dependencies.py
from fastapi import Depends, HTTPException, status
from config.database import DatabaseManager
from backend.services.ai_service import AIService
from backend.services.template_service import TemplateService
from backend.services.coordinator_service import FormService

def get_database() -> DatabaseManager:
    """Get database dependency"""
    return DatabaseManager()

def get_ai_service() -> AIService:
    """Get AI service dependency"""
    return AIService()

def get_template_service() -> TemplateService:
    """Get template service dependency"""
    return TemplateService()

def get_form_service() -> FormService:
    """Get form service dependency"""
    return FormService()