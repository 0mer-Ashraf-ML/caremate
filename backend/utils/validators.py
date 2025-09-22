# backend/utils/validators.py
import re
from typing import Dict, Any, List
from email_validator import validate_email, EmailNotValidError

def validate_user_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate user input data"""
    errors = {}
    
    # Email validation
    if 'email' in data:
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            errors.setdefault('email', []).append("Invalid email format")
    
    # Phone validation
    if 'phone' in data:
        phone_pattern = "r'^\+?[\d\s\-\(\)]+"
        if not re.match(phone_pattern, str(data['phone'])):
            errors.setdefault('phone', []).append("Invalid phone number format")
    
    # Required fields check
    required_fields = ['name']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            errors.setdefault(field, []).append(f"{field.title()} is required")
    
    return errors

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove/replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    return filename.strip()

def validate_template_fields(fields_config: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate template fields configuration"""
    errors = {}
    
    if 'fields' not in fields_config:
        errors['fields'] = ["Fields configuration is required"]
        return errors
    
    fields = fields_config['fields']
    if not isinstance(fields, list):
        errors['fields'] = ["Fields must be a list"]
        return errors
    
    # Check each field
    for i, field in enumerate(fields):
        if not isinstance(field, str) or not field.strip():
            errors.setdefault('fields', []).append(f"Field {i+1} must be a non-empty string")
    
    return errors