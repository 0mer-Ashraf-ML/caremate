# frontend/pages/profile.py - FIXED Button Issue
import streamlit as st
from backend.services.coordinator_service import CoordinatorService
from backend.models.coordinator import CoordinatorProfileCreate

def show():
    """Display the coordinator profile page with database integration"""
    st.title("👤 Coordinator Profile")
    
    coordinator_service = CoordinatorService()
    
    # Check if profile exists in database
    coordinator_profile = st.session_state.get("coordinator_profile") or {}
    profile_complete = False
    
    if coordinator_profile and isinstance(coordinator_profile, dict):
        profile_complete = coordinator_profile.get('profile_complete', False)
    
    # Load existing profile from database if available
    if profile_complete and coordinator_profile.get('id'):
        try:
            db_profile = coordinator_service.get_coordinator_by_id(coordinator_profile['id'])
            if db_profile:
                # Update session state with latest database data
                st.session_state.coordinator_profile = {
                    'id': db_profile.id,
                    'provider_name': db_profile.provider_name,
                    'coordinator_name': db_profile.coordinator_name,
                    'email': db_profile.email,
                    'phone': db_profile.phone,
                    'profile_complete': db_profile.profile_complete,
                    'credits_balance': db_profile.credits_balance,
                    'created_at': str(db_profile.created_at),
                    'updated_at': str(db_profile.updated_at)
                }
                coordinator_profile = st.session_state.coordinator_profile
        except Exception as e:
            st.error(f"Error loading profile from database: {e}")
    
    if profile_complete:
        st.success("✅ Profile Complete")
        
        # Display current profile
        st.subheader("📋 Current Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Provider Name:** {coordinator_profile.get('provider_name')}")
            st.write(f"**Coordinator Name:** {coordinator_profile.get('coordinator_name')}")
        
        with col2:
            st.write(f"**Email:** {coordinator_profile.get('email')}")
            st.write(f"**Phone:** {coordinator_profile.get('phone', 'Not provided')}")
        
        st.write(f"**Credits Balance:** {coordinator_profile.get('credits_balance', 0)}")
        
        # Edit profile option
        if st.button("✏️ Edit Profile"):
            st.session_state.editing_profile = True
            st.rerun()
        
        # Show edit form if editing
        if st.session_state.get('editing_profile', False):
            st.divider()
            show_edit_profile_form(coordinator_service, coordinator_profile)
        
        return
    
    # Profile creation form
    st.markdown("### Complete your coordinator profile to get started")
    st.info("This information will be used in all generated documents and must be completed before creating client folders.")
    
    show_create_profile_form(coordinator_service)

def show_create_profile_form(coordinator_service):
    """Show profile creation form - FIXED VERSION"""
    
    # Form for data input only
    with st.form("coordinator_profile_form", clear_on_submit=False):
        st.subheader("📋 Coordinator Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            provider_name = st.text_input(
                "Provider/Organization Name *",
                help="The name of your NDIS service provider organization",
                key="new_provider_name"
            )
            
            coordinator_name = st.text_input(
                "Your Full Name *",
                help="Your name as it should appear on documents",
                key="new_coordinator_name"
            )
        
        with col2:
            email = st.text_input(
                "Email Address *",
                help="Your professional email address",
                key="new_email"
            )
            
            phone = st.text_input(
                "Phone Number",
                help="Your contact phone number (optional)",
                key="new_phone"
            )
        
        # Only form submit button inside form
        submitted = st.form_submit_button("💾 Save Profile", type="primary")
    
    # Handle form submission
    if submitted:
        # Validation
        if not provider_name or not coordinator_name or not email:
            st.error("❌ Please fill in all required fields (marked with *)")
            return
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            st.error("❌ Please enter a valid email address")
            return
        
        try:
            with st.spinner("Saving profile to database..."):
                # Create profile data model
                profile_data = CoordinatorProfileCreate(
                    provider_name=provider_name,
                    coordinator_name=coordinator_name,
                    email=email,
                    phone=phone or ""
                )
                
                # Save to database
                created_profile = coordinator_service.create_coordinator_profile(profile_data)
                
                # Update session state with database profile
                st.session_state.coordinator_profile = {
                    'id': created_profile.id,
                    'provider_name': created_profile.provider_name,
                    'coordinator_name': created_profile.coordinator_name,
                    'email': created_profile.email,
                    'phone': created_profile.phone,
                    'profile_complete': created_profile.profile_complete,
                    'credits_balance': created_profile.credits_balance,
                    'created_at': str(created_profile.created_at),
                    'updated_at': str(created_profile.updated_at)
                }
            
            st.success("✅ Profile created and saved to database successfully!")
            st.balloons()
            
            # Show success message
            st.info("Profile saved! You can now create client folders and generate documents.")
            
        except Exception as e:
            st.error(f"❌ Error saving profile to database: {str(e)}")
    
    # Action buttons OUTSIDE the form (after form submission is processed)
    if (st.session_state.get("coordinator_profile") or {}).get("profile_complete"):
        st.divider()
        st.markdown("### 🚀 Next Steps")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👥 Create Your First Client", type="primary", use_container_width=True):
                st.session_state.current_page = 'clients'
                st.session_state.show_create_client = True
                st.rerun()
        
        with col2:
            if st.button("📋 Browse Templates", use_container_width=True):
                st.session_state.current_page = 'templates'
                st.rerun()

def show_edit_profile_form(coordinator_service, current_profile):
    """Show profile editing form - FIXED VERSION"""
    st.subheader("✏️ Edit Profile")
    
    # Form for data input only
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            provider_name = st.text_input(
                "Provider/Organization Name *",
                value=current_profile.get('provider_name', ''),
                key="edit_provider_name"
            )
            
            coordinator_name = st.text_input(
                "Your Full Name *",
                value=current_profile.get('coordinator_name', ''),
                key="edit_coordinator_name"
            )
        
        with col2:
            email = st.text_input(
                "Email Address *",
                value=current_profile.get('email', ''),
                key="edit_email"
            )
            
            phone = st.text_input(
                "Phone Number",
                value=current_profile.get('phone', ''),
                key="edit_phone"
            )
        
        # Only form submit buttons inside form
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Update Profile", type="primary")
        with col2:
            cancelled = st.form_submit_button("❌ Cancel")
    
    # Handle form submissions OUTSIDE the form
    if cancelled:
        st.session_state.editing_profile = False
        st.rerun()
    
    if submitted:
        if not provider_name or not coordinator_name or not email:
            st.error("❌ Please fill in all required fields")
            return
        
        try:
            with st.spinner("Updating profile in database..."):
                # Update profile in database
                from config.database import DatabaseManager
                db = DatabaseManager()
                
                update_query = """
                    UPDATE coordinator_profiles 
                    SET provider_name = ?, coordinator_name = ?, email = ?, phone = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                
                db.execute_query(update_query, (
                    provider_name, coordinator_name, email, phone,
                    current_profile['id']
                ))
                
                # Update session state
                st.session_state.coordinator_profile.update({
                    'provider_name': provider_name,
                    'coordinator_name': coordinator_name,
                    'email': email,
                    'phone': phone
                })
                
                st.session_state.editing_profile = False
            
            st.success("✅ Profile updated successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error updating profile: {str(e)}")