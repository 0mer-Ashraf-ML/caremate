# backend/utils/helpers.py
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

def generate_secure_filename(original_filename: str, user_id: int = None) -> str:
    """Generate secure filename with timestamp and hash"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Extract extension
    parts = original_filename.split('.')
    extension = parts[-1] if len(parts) > 1 else 'txt'
    
    # Create hash
    hash_input = f"{original_filename}_{timestamp}_{user_id or 0}_{secrets.token_hex(8)}"
    file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    return f"doc_{timestamp}_{file_hash}.{extension}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def clean_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate JSON data"""
    cleaned = {}
    
    for key, value in data.items():
        # Clean key
        clean_key = str(key).strip().lower().replace(' ', '_')
        
        # Clean value
        if isinstance(value, str):
            clean_value = value.strip()
        elif isinstance(value, (int, float, bool)):
            clean_value = value
        elif isinstance(value, (list, dict)):
            clean_value = value
        else:
            clean_value = str(value).strip()
        
        if clean_key and clean_value:
            cleaned[clean_key] = clean_value
    
    return cleaned

def extract_text_content(content: str) -> str:
    """Extract clean text from markdown/html content"""
    import re
    
    # Remove markdown headers
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    
    # Remove markdown bold/italic
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = re.sub(r'\*(.*?)\*', r'\1', content)
    
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up whitespace
    content = re.sub(r'\n+', '\n', content)
    content = content.strip()
    
    return content