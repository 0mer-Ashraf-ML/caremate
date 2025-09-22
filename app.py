# app.py (Updated for NDIS Support Coordination - Fixed Navigation)
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.pages import home, profile, clients, templates, generate, editor, history, billing
from config.setting import load_config
from config.database import init_database

# Page configuration
st.set_page_config(
    page_title="NDIS Support Coordinator - Document Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    # Initialize database
    init_database()
    
    # Load configuration
    config = load_config()
    
    # Initialize session state
    if 'coordinator_profile' not in st.session_state:
        st.session_state.coordinator_profile = None
    if 'current_client' not in st.session_state:
        st.session_state.current_client = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Check if profile is complete
    profile_complete = (
        st.session_state.coordinator_profile and 
        st.session_state.coordinator_profile.get('profile_complete', False)
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📋 NDIS Document Generator")
        st.markdown("*Support Coordination Assistant*")
        st.divider()
        
        # Profile status
        if profile_complete:
            coordinator = st.session_state.coordinator_profile
            st.success("✅ Profile Complete")
            st.write(f"👤 {coordinator.get('coordinator_name')}")
            st.write(f"🏢 {coordinator.get('provider_name')}")
            st.write(f"💰 Credits: {coordinator.get('credits_balance', 0)}")
        else:
            st.warning("⚠️ Complete profile first")
        
        st.divider()
        
        # Navigation based on profile status
        if not profile_complete:
            page_options = ['home', 'profile']
        else:
            page_options = ['home', 'profile', 'clients', 'templates', 'history', 'billing']
        
        page = st.selectbox(
            "Navigate:",
            options=page_options,
            format_func=lambda x: {
                'home': '🏠 Home',
                'profile': '👤 Profile', 
                'clients': '👥 Clients',
                'templates': '📋 Templates',
                'history': '📚 History',
                'billing': '💳 Credits'
            }[x]
        )
        
        # Only override session_state if NOT in workflow pages
        if st.session_state.current_page not in ["generate", "editor"]:
            st.session_state.current_page = page
        
        st.divider()
        
        # Quick stats
        if profile_complete:
            st.markdown("**Quick Stats**")
            st.metric("Active Clients", len(st.session_state.get('client_list', [])))
            st.metric("Documents This Month", len(st.session_state.get('recent_documents', [])))
        
        # Help section
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Getting Started:**
            1. Complete your coordinator profile
            2. Create client folders
            3. Upload relevant documents
            4. Select templates and generate reports
            
            **Document Types:**
            - Change of Circumstance
            - Implementation Report  
            - Progress Report
            - Support Plan
            - Assessment
            """)
    
    # Route to appropriate page
    if st.session_state.current_page == 'home':
        home.show()
    elif st.session_state.current_page == 'profile':
        profile.show()
    elif st.session_state.current_page == 'clients':
        clients.show()
    elif st.session_state.current_page == 'templates':
        templates.show()
    elif st.session_state.current_page == 'generate':
        generate.show()
    elif st.session_state.current_page == 'editor':
        editor.show()
    elif st.session_state.current_page == 'history':
        history.show()
    elif st.session_state.current_page == 'billing':
        billing.show()

if __name__ == "__main__":
    main()
