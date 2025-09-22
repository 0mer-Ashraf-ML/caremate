# frontend/utils/ui_helpers.py
import streamlit as st
from typing import Dict, Any, List, Optional
import json

def display_user_data_form() -> Dict[str, Any]:
    """Display and collect user data input form"""
    st.subheader("📝 Enter Your Information")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Personal Information**")
        name = st.text_input("Full Name", key="name")
        email = st.text_input("Email Address", key="email") 
        phone = st.text_input("Phone Number", key="phone")
        address = st.text_area("Address", key="address", height=100)
    
    with col2:
        st.markdown("**Professional Information**")
        job_title = st.text_input("Job Title", key="job_title")
        company = st.text_input("Company", key="company")
        experience = st.selectbox(
            "Years of Experience",
            ["0-1", "2-5", "6-10", "11-15", "16+"],
            key="experience"
        )
        skills = st.text_area("Skills (comma-separated)", key="skills", height=100)
    
    # Additional information
    st.markdown("**Additional Information**")
    additional_info = st.text_area(
        "Any additional information you'd like to include:",
        height=100,
        key="additional_info"
    )
    
    # Collect all data
    user_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "job_title": job_title,
        "company": company,
        "experience": experience,
        "skills": [skill.strip() for skill in skills.split(",") if skill.strip()],
        "additional_info": additional_info
    }
    
    # Remove empty values
    return {k: v for k, v in user_data.items() if v}

def display_template_suggestions(suggestions: List[Dict[str, Any]]) -> Optional[int]:
    """Display template suggestions and allow selection"""
    if not suggestions:
        st.warning("No template suggestions found.")
        return None
    
    st.subheader("🎯 Suggested Templates")
    
    selected_template_id = None
    
    for i, suggestion in enumerate(suggestions):
        template = suggestion.get('template', {})
        match_score = suggestion.get('match_score', 0)
        reasoning = suggestion.get('reasoning', '')
        
        with st.expander(f"📋 {template.get('name', 'Unknown Template')} (Match: {match_score:.0%})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Category:** {template.get('category', 'N/A')}")
                st.write(f"**Description:** {template.get('description', 'No description available')}")
                if reasoning:
                    st.write(f"**Why this matches:** {reasoning}")
            
            with col2:
                if st.button(f"Select", key=f"select_{template.get('id')}"):
                    selected_template_id = template.get('id')
                    st.success("Template selected!")
    
    return selected_template_id

def display_progress_bar(step: int, total_steps: int, step_names: List[str]):
    """Display progress bar for multi-step process"""
    progress = step / total_steps
    st.progress(progress)
    
    # Display step names
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names)):
        with col:
            if i < step:
                st.write(f"✅ {step_name}")
            elif i == step:
                st.write(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")

def display_form_preview(populated_fields: Dict[str, Any], template_name: str):
    """Display preview of populated form"""
    st.subheader(f"👀 Preview: {template_name}")
    
    with st.container():
        st.markdown("**Form Fields:**")
        
        for field_name, field_value in populated_fields.items():
            if field_value:
                st.write(f"**{field_name.replace('_', ' ').title()}:** {field_value}")

def show_success_message(message: str, details: Dict[str, Any] = None):
    """Show success message with optional details"""
    st.success(message)
    
    if details:
        with st.expander("📋 Details"):
            for key, value in details.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

def show_error_message(message: str, error_details: str = None):
    """Show error message with optional details"""
    st.error(message)
    
    if error_details and st.checkbox("Show technical details"):
        st.code(error_details)