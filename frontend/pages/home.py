# frontend/pages/home.py
import streamlit as st

def show():
    """Display the home page"""
    st.title("🏠 NDIS Support Coordinator Document Generator")
    
    # Check profile status
    profile_complete = (
        st.session_state.coordinator_profile and 
        st.session_state.coordinator_profile.get('profile_complete', False)
    )
    
    if not profile_complete:
        st.markdown("### 👋 Welcome! Let's get you set up.")
        st.info("Please complete your coordinator profile to start generating NDIS documents.")
        
        if st.button("👤 Setup Profile", type="primary", use_container_width=True):
            st.session_state.current_page = 'profile'
            st.rerun()
        
        return
    
    # Profile complete - show dashboard
    coordinator = st.session_state.coordinator_profile
    
    st.markdown(f"### Welcome back, {coordinator.get('coordinator_name')}! 👋")
    
    # Quick stats dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        client_count = len(st.session_state.get('client_list', []))
        st.metric("Active Clients", client_count)
    
    with col2:
        credits = coordinator.get('credits_balance', 0)
        st.metric("Available Credits", credits)
    
    with col3:
        documents_count = len(st.session_state.get('recent_documents', []))
        st.metric("Documents Generated", documents_count)
    
    with col4:
        st.metric("Templates Available", 5)
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        st.markdown("**Client Management**")
        if st.button("👥 Manage Clients", use_container_width=True):
            st.session_state.current_page = 'clients'
            st.rerun()
        
        if st.button("➕ Add New Client", use_container_width=True):
            st.session_state.current_page = 'clients'
            st.session_state.show_create_client = True
            st.rerun()
    
    with action_col2:
        st.markdown("**Document Generation**")
        if st.button("📋 Browse Templates", use_container_width=True):
            st.session_state.current_page = 'templates'
            st.rerun()
        
        if st.button("📚 View History", use_container_width=True):
            st.session_state.current_page = 'history'
            st.rerun()
    
    st.divider()
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    recent_docs = st.session_state.get('recent_documents', [])
    if recent_docs:
        for doc in recent_docs[-3:]:  # Show last 3
            with st.expander(f"📄 {doc.get('document_name', 'Unknown Document')}"):
                st.write(f"**Client:** {doc.get('client_name', 'Unknown')}")
                st.write(f"**Template:** {doc.get('template_name', 'Unknown')}")
                st.write(f"**Generated:** {doc.get('created_at', 'Unknown')}")
                st.write(f"**Status:** {doc.get('status', 'Unknown')}")
    else:
        st.info("No recent activity. Create your first client folder to get started!")
