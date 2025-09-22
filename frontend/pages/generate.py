# frontend/pages/generate.py
import streamlit as st
from datetime import datetime
import os
from backend.services.document_generation_service import DocumentGenerationService

def show():
    st.title("⚡ Generate Document")
    
    current_client = st.session_state.get('current_client')
    selected_template = st.session_state.get('selected_template')
    coordinator = st.session_state.get('coordinator_profile')
    
    if not current_client or not selected_template:
        st.error("❌ Missing required information.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👥 Select Client"):
                st.session_state.current_page = 'clients'
                st.rerun()
        with col2:
            if st.button("📋 Select Template"):
                st.session_state.current_page = 'templates'
                st.rerun()
        return
    
    st.info(f"📁 **Client:** {current_client['full_name']} | 📋 **Template:** {selected_template['name']}")
    
    # -------- Document generation form --------
    with st.form("document_generation_form"):
        st.subheader("📝 Document Context")
        
        context_description = st.text_area(
            "Reason for this document *",
            height=120,
            placeholder=f"Provide specific context for why you're creating this {selected_template['name']}"
        )
        
        uploaded_files = st.file_uploader(
            "Upload supporting documents (optional)",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True
        )
        
        generate_clicked = st.form_submit_button("⚡ Generate Document", type="primary")

        if generate_clicked:
            if not context_description:
                st.error("❌ Please provide context for the document.")
                return

            st.session_state._generate_request = {
                "template": selected_template,
                "client": current_client,
                "coordinator": coordinator,
                "context": context_description,
                "uploaded_files": uploaded_files or []
            }

    # -------- Outside form: handle request --------
    if "_generate_request" in st.session_state:
        req = st.session_state.pop("_generate_request")
        with st.spinner("🤖 AI is generating your document..."):
            try:
                service = DocumentGenerationService()
                template_obj = req["template"]

                # Handle template_type safely
                template_type = template_obj.get("type") or template_obj.get("template_type")
                if not template_type:
                    raise ValueError(f"Template type missing in selected template: {template_obj}")

                result = service.generate_docx_document(
                    client_id=req["client"]["id"],
                    template_type=template_type,
                    context=req["context"],
                    coordinator_data=req["coordinator"]
                )

                if result:
                    # Deduct credits
                    coordinator['credits_balance'] -= 10
                    st.session_state.coordinator_profile = coordinator
                    
                    # Save record
                    doc_record = {
                        'id': result["document_id"],
                        'document_name': result['document_name'],
                        'client_name': result['client_name'],
                        'template_name': selected_template['name'],
                        'content': result['content'],
                        'output_path': result['output_path'],  # ✅ already has .docx
                        'version': 1,
                        'status': 'draft',
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'credits_used': 10
                    }
                    
                    if 'recent_documents' not in st.session_state:
                        st.session_state.recent_documents = []
                    st.session_state.recent_documents.append(doc_record)
                    
                    st.success("✅ Document generated successfully!")
                    st.balloons()
                    
                    # ✅ Download button (use exact file path, no extra .docx added)
                    if result.get("output_path") and os.path.exists(result["output_path"]):
                        with open(result["output_path"], "rb") as f:
                            st.download_button(
                                label="⬇️ Download Document",
                                data=f,
                                file_name=os.path.basename(result["output_path"]),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    
                    # Redirect to editor
                    st.session_state.current_document = doc_record
                    st.session_state.current_page = 'editor'
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating document: {str(e)}")
