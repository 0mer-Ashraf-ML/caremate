# frontend/pages/templates.py
import streamlit as st
from backend.services.extraction_service import ExtractionService
from backend.services.document_generation_service import DocumentGenerationService
import json


def show():
    """Templates page – run extraction & generate documents"""
    st.title("📑 Templates & Document Generation")

    if not st.session_state.get("current_client"):
        st.warning("⚠️ Please select a client first from the Clients page.")
        return

    client = st.session_state.current_client
    client_id = client["id"]
    st.subheader(f"👤 Current Client: {client['full_name']} (NDIS: {client['ndis_number']})")

    extractor = ExtractionService()
    generator = DocumentGenerationService()

    # ---- Step 1: Choose Template Type ----
    template_type = st.selectbox(
        "📌 Select Template Type",
        ["change_of_circumstance", "progress_report", "implementation_report", "support_plan"]
    )

    st.markdown("---")

    # ---- Step 2: Run Gemini Extraction ----
    st.markdown("### 🧠 Run Extraction with Gemini")

    if st.button("⚡ Run Extraction"):
        try:
            structured = extractor.process_with_schema(client_id, template_type)
            st.success("✅ Extraction completed successfully!")

            # Show extracted JSON
            st.json(structured.get("extracted", {}))

            # Show Markdown preview
            st.markdown("### 📄 Extracted Summary")
            st.markdown(structured.get("markdown_summary", ""))

        except Exception as e:
            st.error(f"❌ Error running extraction: {e}")

    st.markdown("---")

    # ---- Step 3: Generate DOCX ----
    st.markdown("### 📄 Generate Word Document")

    context_notes = st.text_area("Add extra context (optional)")
    coordinator_data = st.session_state.coordinator_profile or {}

    if st.button("📝 Generate Document"):
        try:
            result = generator.generate_docx_document(
                client_id=client_id,
                template_type=template_type,
                context=context_notes,
                coordinator_data=coordinator_data,
            )
            st.success(f"✅ Document generated: {result['document_name']}")
            st.write(f"📂 Saved at: {result['output_path']}")

        except Exception as e:
            st.error(f"❌ Error generating document: {e}")
