# backend/services/template_service.py
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from config.database import DatabaseManager

class TemplateService:
    """Service for managing DOCX NDIS document templates"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.template_dir = Path("./templates/docx_templates")
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_templates_in_db()
    
    def ensure_templates_in_db(self):
        """Ensure templates are seeded in DB"""
        existing_templates = self.db.execute_query("SELECT COUNT(*) FROM document_templates")
        if not existing_templates or existing_templates[0][0] == 0:
            self._populate_docx_templates()
    
    def _populate_docx_templates(self):
        """Populate database with DOCX template references"""
        docx_templates = [
            {
                "name": "Change of Circumstance",
                "template_type": "change_of_circumstance",
                "template_path": "./templates/docx_templates/change_of_circumstances.docx",
                "description": "Document changes in participant circumstances requiring plan review",
                "fields_config": {
                    "template_variables": [
                        "participant_name", "ndis_number", "plan_start_date", "plan_end_date",
                        "coordinator_name", "provider_name", "coordinator_email", "coordinator_phone",
                        "current_date", "change_type", "change_description", "impact_assessment",
                        "recommendations", "next_steps"
                    ],
                    "required_fields": ["participant_name", "ndis_number", "change_description"],
                    "categories": ["circumstances", "plan_review", "support_changes"]
                }
            },
            {
                "name": "Implementation Report",
                "template_type": "implementation_report", 
                "template_path": "./templates/docx_templates/implementation_report.docx",
                "description": "Report on NDIS plan implementation progress and outcomes",
                "fields_config": {
                    "template_variables": [
                        "participant_name", "ndis_number", "plan_start_date", "plan_end_date",
                        "coordinator_name", "provider_name", "reporting_period", "initial_contact_date",
                        "contact_frequency", "goal_1", "goal_2", "goal_3", "goal_1_progress",
                        "goal_2_progress", "goal_3_progress", "implementation_activities"
                    ],
                    "required_fields": ["participant_name", "ndis_number", "reporting_period"],
                    "categories": ["implementation", "progress", "coordination"]
                }
            },
            {
                "name": "Progress Report",
                "template_type": "progress_report",
                "template_path": "./templates/docx_templates/progress_report.docx", 
                "description": "Regular progress report on participant goals and support outcomes",
                "fields_config": {
                    "template_variables": [
                        "participant_name", "ndis_number", "plan_start_date", "plan_end_date",
                        "coordinator_name", "provider_name", "current_date", "reporting_period",
                        "progress_summary", "achievements", "challenges", "goal_progress",
                        "community_supports", "funded_supports", "next_steps"
                    ],
                    "required_fields": ["participant_name", "ndis_number", "progress_summary"],
                    "categories": ["progress", "goals", "outcomes"]
                }
            },
            {
                "name": "Support Plan", 
                "template_type": "support_plan",
                "template_path": "./templates/docx_templates/support_plan.docx",
                "description": "Comprehensive support plan outlining services and strategies",
                "fields_config": {
                    "template_variables": [
                        "participant_name", "ndis_number", "date_of_birth", "address", "phone",
                        "email", "coordinator_name", "provider_name", "referral_date", "services_requested",
                        "goals", "support_strategies", "risk_assessment", "about_me", "key_people",
                        "health_information", "communication_preferences"
                    ],
                    "required_fields": ["participant_name", "ndis_number", "services_requested"],
                    "categories": ["planning", "coordination", "risk_management"]
                }
            },
            {
                "name": "Assessment",
                "template_type": "assessment",
                "template_path": "./templates/docx_templates/assessment.docx",
                "description": "Formal assessment of participant needs and capacity",
                "fields_config": {
                    "template_variables": [
                        "participant_name", "ndis_number", "assessment_date", "assessment_purpose",
                        "living_situation", "daily_living_skills", "communication_abilities", 
                        "mobility_assessment", "support_needs", "recommendations", "next_steps",
                        "coordinator_name", "provider_name", "current_date"
                    ],
                    "required_fields": ["participant_name", "ndis_number", "assessment_purpose"],
                    "categories": ["assessment", "capacity", "needs_analysis"]
                }
            }
        ]
        
        for template in docx_templates:
            query = """
                INSERT OR IGNORE INTO document_templates 
                (name, template_type, template_path, description, fields_config, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_insert(query, (
                template["name"],
                template["template_type"],
                template["template_path"], 
                template["description"],
                json.dumps(template["fields_config"]),
                True
            ))
    
    def get_all_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all DOCX templates from database"""
        query = "SELECT * FROM document_templates"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        
        results = self.db.execute_query(query)
        templates = []
        
        for row in results:
            template = dict(row)
            if template['fields_config']:
                try:
                    template['fields_config'] = json.loads(template['fields_config'])
                except:
                    template['fields_config'] = {}
            templates.append(template)
        
        return templates
    
    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get template by ID"""
        query = "SELECT * FROM document_templates WHERE id = ?"
        results = self.db.execute_query(query, (template_id,))
        
        if not results:
            return None
        
        template = dict(results[0])
        if template['fields_config']:
            try:
                template['fields_config'] = json.loads(template['fields_config'])
            except:
                template['fields_config'] = {}
        
        return template

    def get_template_by_type(self, template_type: str) -> Optional[Dict[str, Any]]:
        """Get template by type (progress_report, assessment, etc.)"""
        query = "SELECT * FROM document_templates WHERE template_type = ?"
        results = self.db.execute_query(query, (template_type,))
        
        if not results:
            return None
        
        template = dict(results[0])
        if template['fields_config']:
            try:
                template['fields_config'] = json.loads(template['fields_config'])
            except:
                template['fields_config'] = {}
        
        return template
