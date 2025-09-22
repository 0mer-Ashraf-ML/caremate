# frontend/components/file_upload.py
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any
import os

def handle_file_upload(client_id: int, allowed_types: List[str] = None) -> List[Dict[str, Any]]:
    """Handle file upload for client documents"""
    
    if allowed_types is None:
        allowed_types = ['pdf', 'docx', 'txt']
    
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=allowed_types,
        accept_multiple_files=True,
        help="Upload OT reports, NDIS plans, medical reports, or other relevant documents"
    )
    
    uploaded_docs = []
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Create upload directory if it doesn't exist
            upload_dir = Path("./uploads/client_documents")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = upload_dir / f"client_{client_id}_{uploaded_file.name}"
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Mock document processing
            doc_info = {
                'id': len(uploaded_docs) + 1,
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.type,
                'file_path': str(file_path),
                'extracted_content': f"Mock extracted content from {uploaded_file.name}",
                'summary': f"AI-generated summary of {uploaded_file.name}"
            }
            
            uploaded_docs.append(doc_info)
    
    return uploaded_docs

def show_document_preview(document: Dict[str, Any]):
    """Show document preview and summary"""
    
    with st.expander(f"📄 {document['name']}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Type:** {document.get('type', 'Unknown')}")
            st.write(f"**Size:** {document.get('size', 'Unknown')} bytes")
            
            if document.get('summary'):
                st.write("**AI Summary:**")
                st.info(document['summary'])
        
        with col2:
            if st.button(f"🗑️ Remove", key=f"remove_{document['id']}"):
                return True  # Signal to remove document
            
            if st.button(f"📥 Download", key=f"download_{document['id']}"):
                # Mock download
                st.success("Download started!")
    
    return False
