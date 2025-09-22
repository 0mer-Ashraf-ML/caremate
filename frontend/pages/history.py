# frontend/pages/history.py
import streamlit as st
import os
from datetime import datetime

def show():
    """Display the document history page"""
    st.title("📚 Document History")
    
    # Get recent documents
    recent_docs = st.session_state.get('recent_documents', [])
    
    if not recent_docs:
        st.info("📝 No documents generated yet.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👥 Create Client"):
                st.session_state.current_page = 'clients'
                st.rerun()
        
        with col2:
            if st.button("📋 Browse Templates"):
                st.session_state.current_page = 'templates'  
                st.rerun()
        
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", len(recent_docs))
    
    with col2:
        draft_count = sum(1 for doc in recent_docs if doc.get('status') == 'draft')
        st.metric("Draft Documents", draft_count)
    
    with col3:
        final_count = sum(1 for doc in recent_docs if doc.get('status') == 'final')
        st.metric("Final Documents", final_count)
    
    with col4:
        total_credits = sum(doc.get('credits_used', 0) for doc in recent_docs)
        st.metric("Credits Used", total_credits)
    
    st.divider()
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Draft", "Final"]
        )
    
    with col2:
        template_filter = st.selectbox(
            "Filter by Template", 
            ["All"] + list(set(doc.get('template_name', '') for doc in recent_docs))
        )
    
    with col3:
        client_filter = st.selectbox(
            "Filter by Client",
            ["All"] + list(set(doc.get('client_name', '') for doc in recent_docs))
        )
    
    # Apply filters
    filtered_docs = recent_docs.copy()
    
    if status_filter != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('status', '').lower() == status_filter.lower()]
    
    if template_filter != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('template_name') == template_filter]
    
    if client_filter != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('client_name') == client_filter]
    
    # Display documents
    st.subheader(f"📋 Documents ({len(filtered_docs)})")
    
    for i, doc in enumerate(reversed(filtered_docs)):  # Show newest first
        with st.expander(f"📄 {doc['document_name']} - {doc.get('created_at', 'Unknown date')}"):
            
            doc_col1, doc_col2, doc_col3 = st.columns([2, 1, 1])
            
            with doc_col1:
                st.write(f"**Client:** {doc.get('client_name', 'Unknown')}")
                st.write(f"**Template:** {doc.get('template_name', 'Unknown')}")
                st.write(f"**Version:** {doc.get('version', 1)}")
                st.write(f"**Status:** {doc.get('status', 'draft').title()}")
                st.write(f"**Credits Used:** {doc.get('credits_used', 0)}")
            
            with doc_col2:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.current_document = doc
                    st.session_state.current_page = 'editor'
                    st.rerun()
                
                if st.button("👁️ View", key=f"view_{i}"):
                    st.session_state.viewing_document = doc
            
            with doc_col3:
                # Download options
                if st.button("📄 Download PDF", key=f"pdf_{i}"):
                    # Mock PDF download
                    st.success("PDF downloaded!")
                
                if st.button("📝 Download DOCX", key=f"docx_{i}"):
                    # Mock DOCX download  
                    st.success("DOCX downloaded!")
                
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    # Remove from history
                    st.session_state.recent_documents.remove(doc)
                    st.success("Document deleted!")
                    st.rerun()
    
    # Bulk actions
    if len(filtered_docs) > 1:
        st.divider()
        st.subheader("🔧 Bulk Actions")
        
        bulk_col1, bulk_col2 = st.columns(2)
        
        with bulk_col1:
            if st.button("📦 Export All Documents"):
                # Mock export functionality
                st.success("All documents exported!")
        
        with bulk_col2:
            if st.button("🗑️ Clear History", type="secondary"):
                if st.checkbox("⚠️ Confirm deletion"):
                    st.session_state.recent_documents = []
                    st.success("History cleared!")
                    st.rerun()