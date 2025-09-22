# frontend/pages/clients.py
import streamlit as st
from datetime import datetime
from backend.services.client_service import ClientService
from backend.models.client import ClientFolderCreate, ClientFolder
import json
from backend.services.extraction_service import ExtractionService
import os
import tempfile
from config.database import DatabaseManager


def show():
    """Display the clients management page"""
    st.title("👥 Client Management")

    if not st.session_state.coordinator_profile:
        st.warning("⚠️ Please complete your coordinator profile first.")
        return

    coordinator_id = st.session_state.coordinator_profile['id']
    client_service = ClientService()

    # ✅ Always fetch from DB
    client_list = client_service.get_coordinator_clients(coordinator_id)

    tab1, tab2 = st.tabs(["📋 Client List", "➕ Add New Client"])

    # -------- Tab 1: List clients --------
    with tab1:
        if not client_list:
            st.info("📝 No clients created yet. Add your first client to get started!")
        else:
            st.subheader(f"📋 Your Clients ({len(client_list)})")

            for i, client in enumerate(client_list):
                with st.expander(f"👤 {client.full_name} (NDIS: {client.ndis_number})"):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.write(f"**Email:** {client.email or 'Not provided'}")
                        st.write(f"**Phone:** {client.phone or 'Not provided'}")
                        st.write(
                            f"**Plan Period:** {client.plan_start_date or 'N/A'} → {client.plan_end_date or 'N/A'}"
                        )

                    with col2:
                        if client.conditions:
                            st.write(f"**Conditions:** {', '.join(client.conditions)}")

                        goals = []
                        if client.goals_advocacy:
                            goals.append("Advocacy")
                        if client.goals_support:
                            goals.append("Support")
                        if client.goals_capacity_building:
                            goals.append("Capacity Building")
                        if client.goals_funding_increase:
                            goals.append("Funding Increase")
                        if client.goals_other:
                            goals.append(client.goals_other)

                        if goals:
                            st.write(f"**Goals:** {', '.join(goals)}")

                    with col3:
                        if st.button("➡️ Select Client", key=f"select_{i}"):
                            fresh_client = client_service.get_client_by_id(client.id)
                            st.session_state.current_client = fresh_client.dict()
                            st.session_state.current_page = "templates"
                            st.rerun()

                        if st.button("✏️ Edit", key=f"edit_{i}"):
                            st.session_state.editing_client = client.dict()
                            st.session_state.show_edit_form = True
                            st.rerun()

                        if st.button("📄 View Files", key=f"files_{i}"):
                            show_client_documents(client)

    # -------- Tab 2: Add new client --------
    with tab2:
        show_create_client_form(coordinator_id, client_service)


def show_create_client_form(coordinator_id: int, client_service: ClientService):
    """Show form to create new client"""
    st.subheader("➕ Create New Client Folder")

    with st.form("create_client_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *")
            ndis_number = st.text_input("NDIS Number *")
            email = st.text_input("Email Address")
        with col2:
            phone = st.text_input("Phone Number")
            plan_start = st.date_input("Plan Start Date")
            plan_end = st.date_input("Plan End Date")

        selected_conditions = st.multiselect(
            "Conditions",
            [
                "Autism Spectrum Disorder",
                "Intellectual Disability",
                "Physical Disability",
                "Psychosocial Disability",
                "Sensory Disability",
                "Acquired Brain Injury",
                "Other",
            ],
        )
        other_conditions = st.text_input("Other Conditions")
        if other_conditions:
            selected_conditions.append(other_conditions)

        goals_advocacy = st.checkbox("Advocacy")
        goals_support = st.checkbox("Support")
        goals_capacity_building = st.checkbox("Capacity Building")
        goals_funding_increase = st.checkbox("Funding Increase")
        goals_other = st.text_area("Other Goals/Needs")
        coordinator_notes = st.text_area("Coordinator Notes")

        # ✅ Upload OT/NDIS report at creation
        uploaded_doc = st.file_uploader(
            "📤 Upload initial document (optional)",
            type=["pdf", "docx", "txt"],
            help="Upload OT Report, NDIS Plan, etc."
        )

        submitted = st.form_submit_button("💾 Create Client Folder", type="primary")

        if submitted:
            if not full_name or not ndis_number:
                st.error("❌ Full Name and NDIS Number required.")
                return

            try:
                # Step 1: Save client
                client_data = ClientFolderCreate(
                    coordinator_id=coordinator_id,
                    full_name=full_name,
                    ndis_number=ndis_number,
                    plan_start_date=plan_start.isoformat(),
                    plan_end_date=plan_end.isoformat(),
                    email=email,
                    phone=phone,
                    conditions=selected_conditions,
                    coordinator_notes=coordinator_notes,
                    goals_advocacy=goals_advocacy,
                    goals_support=goals_support,
                    goals_capacity_building=goals_capacity_building,
                    goals_funding_increase=goals_funding_increase,
                    goals_other=goals_other,
                )
                new_client = client_service.create_client_folder(client_data)

                # Step 2: If document uploaded → only store raw text
                if uploaded_doc:
                    tmp_dir = tempfile.mkdtemp()
                    file_path = os.path.join(tmp_dir, uploaded_doc.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_doc.getbuffer())

                    extractor = ExtractionService()
                    template_type = "change_of_circumstance"  # default guess
                    extractor.store_raw_document(
                        client_id=new_client.id,
                        template_type=template_type,
                        file_path=file_path
                    )

                    st.success(f"✅ Document uploaded & raw text stored for {template_type}")

                # Success
                st.session_state.client_created = new_client.full_name
                st.session_state.current_client = new_client.model_dump()

            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ✅ After form, show success message
    if st.session_state.get("client_created"):
        st.success(f"✅ Client created: {st.session_state.client_created}")
        st.balloons()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➡️ Go to Templates"):
                st.session_state.current_page = "templates"
                st.session_state.pop("client_created", None)
                st.rerun()
        with col2:
            if st.button("➕ Add Another Client"):
                st.session_state.pop("client_created", None)
                st.rerun()


def show_client_documents(client):
    """Show client documents in modal"""
    st.subheader(f"📄 Documents for {client.full_name}")

    db = DatabaseManager()
    query = """
        SELECT id, template_type, extracted_json, markdown_summary, raw_json, created_at
        FROM client_extracted_data
        WHERE client_id = ?
        ORDER BY created_at DESC
    """
    rows = db.execute_query(query, (client.id,))

    if not rows:
        st.info("📁 No documents uploaded yet.")
    else:
        for row in rows:
            with st.expander(f"📄 {row['template_type']} (Uploaded: {row['created_at']})"):
                if row["markdown_summary"]:
                    st.markdown(f"**AI Summary:**\n\n{row['markdown_summary']}")
                if row["extracted_json"]:
                    try:
                        st.json(json.loads(row["extracted_json"]))
                    except:
                        st.text(row["extracted_json"])
                if not row["extracted_json"]:
                    st.warning("⚠️ Extraction not yet processed. Run from Templates page.")

    # ---- Upload new document ----
    st.markdown("**📤 Upload New Document**")
    uploaded_file = st.file_uploader(
        "Choose file",
        type=["pdf", "docx", "txt"],
        help="Upload OT reports, NDIS plans, or other relevant documents"
    )

    if uploaded_file:
        doc_type = st.selectbox(
            "Document Type",
            ["OT Report", "NDIS Plan", "Psychology Report", "Medical Report", "Other"]
        )

        if st.button("📤 Upload & Store Raw"):
            try:
                tmp_dir = tempfile.mkdtemp()
                file_path = os.path.join(tmp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                extractor = ExtractionService()
                template_type = "change_of_circumstance" if doc_type == "OT Report" else "progress_report"
                extractor.store_raw_document(
                    client_id=client.id,
                    template_type=template_type,
                    file_path=file_path
                )

                st.success(f"✅ {uploaded_file.name} uploaded & raw text stored.")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error during upload: {str(e)}")
