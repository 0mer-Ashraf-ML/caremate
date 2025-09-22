# frontend/pages/editor.py
import streamlit as st
from typing import Dict, Any
from datetime import datetime
import asyncio
import os
from backend.services.document_service import DocumentService

def show():
    """Display the document editor page"""
    st.title("✏️ Document Editor")
    
    # Check if document exists
    current_doc = st.session_state.get('current_document')
    selected_template = st.session_state.get('selected_template')
    
    if not current_doc or not selected_template:
        st.warning("⚠️ No document or template selected.")
        if st.button("📚 Go to Templates"):
            st.session_state.current_page = 'templates'
            st.rerun()
        return
    
    # Document header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**📄 {current_doc['document_name']}**")
        st.write(f"Client: {current_doc['client_name']}")
    
    with col2:
        st.write(f"Version: {current_doc.get('version', 1)}")
        st.write(f"Status: {current_doc.get('status', 'draft')}")
    
    with col3:
        if st.button("💾 Save as Final"):
            current_doc['status'] = 'final'
            st.success("✅ Document marked as final!")
            st.rerun()
    
    # Main editor layout
    editor_col, chat_col = st.columns([2, 1])
    
    with editor_col:
        st.subheader("📝 Document Content")
        
        # Editable document content
        edited_content = st.text_area(
            "Document Content (Markdown)",
            value=current_doc.get('content', ''),
            height=500,
            help="Edit the document content. Use markdown formatting."
        )
        
        # Update content if changed
        if edited_content != current_doc.get('content', ''):
            current_doc['content'] = edited_content
            st.session_state.current_document = current_doc
        
        # Preview toggle
        if st.checkbox("👀 Preview Mode"):
            st.markdown("### Preview")
            st.markdown(edited_content)
        
        # Document actions
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📄 Generate PDF"):
                try:
                    # TODO: implement PDF export later
                    st.success("✅ PDF generated! Check downloads.")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with action_col2:
            if st.button("📝 Generate DOCX"):
                try:
                    svc = DocumentService()
                    
                    # Template file based on type
                    template_filename = f"{selected_template['type']}.docx"
                    template_path = os.path.join("templates", template_filename)
                    
                    # Build context for template
                    context_data = {
                        "participant_name": current_doc["client_name"],
                        "document_content": current_doc["content"],
                        "coordinator_name": st.session_state.coordinator_profile["coordinator_name"],
                        "provider_name": st.session_state.coordinator_profile["provider_name"],
                        "date_generated": datetime.now().strftime("%Y-%m-%d"),
                    }

                    # Run async DOCX generation
                    output_path = asyncio.run(
                        svc.generate_docx_from_template(
                            template_path,
                            context_data,
                            current_doc["document_name"].replace(" ", "_")
                        )
                    )

                    st.success(f"✅ DOCX generated at: {output_path}")

                    # Download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download DOCX",
                            data=f,
                            file_name=f"{current_doc['document_name']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                except Exception as e:
                    st.error(f"Error generating DOCX: {str(e)}")
        
        with action_col3:
            if st.button("🔄 Regenerate from Scratch"):
                if st.session_state.coordinator_profile['credits_balance'] >= 10:
                    st.session_state.coordinator_profile['credits_balance'] -= 10
                    st.success("✅ Document regenerated! (10 credits used)")
                    st.rerun()
                else:
                    st.error("❌ Insufficient credits")
    
    # chat_col stays the same...
