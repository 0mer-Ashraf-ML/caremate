# utils/dev_helpers.py
"""Development helper utilities"""

import json
import os
from pathlib import Path
from datetime import datetime

def create_sample_user_session():
    """Create sample user session data for testing"""
    return {
        "user_data": {
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com", 
            "phone": "555-234-5678",
            "address": "321 Elm Street, Test City, TC 54321",
            "job_title": "Product Manager",
            "company": "Innovation Labs",
            "experience": "6-10",
            "skills": ["Product Strategy", "User Research", "Data Analysis", "Leadership"],
            "additional_info": "Passionate about creating user-centered products"
        },
        "generated_forms": [
            {
                "form_id": 1,
                "template_name": "Employment Application",
                "output_path": "./output/generated/employment_application_20241201_123456.pdf",
                "generated_at": datetime.now().isoformat(),
                "status": "generated"
            }
        ]
    }

def reset_session_state():
    """Reset session state for fresh testing"""
    import streamlit as st
    
    keys_to_reset = [
        'user_data', 'template_suggestions', 'selected_template_id', 
        'generated_forms', 'current_page'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def export_user_data(user_data: dict, filename: str = None):
    """Export user data to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_export_{timestamp}.json"
    
    output_path = Path("./output/temp") / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2)
    
    return str(output_path)

def import_user_data(file_path: str) -> dict:
    """Import user data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
