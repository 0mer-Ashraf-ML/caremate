# frontend/pages/billing.py
import streamlit as st
from datetime import datetime

def show():
    """Display the billing and credits page"""
    st.title("💳 Credits & Billing")
    
    coordinator = st.session_state.get('coordinator_profile')
    
    if not coordinator:
        st.error("❌ Coordinator profile not found.")
        return
    
    # Current balance
    st.subheader("💰 Current Balance")
    
    balance_col1, balance_col2 = st.columns([1, 2])
    
    with balance_col1:
        current_balance = coordinator.get('credits_balance', 0)
        st.metric("Available Credits", current_balance)
        
        # Credit status
        if current_balance > 50:
            st.success("✅ Good credit balance")
        elif current_balance > 20:
            st.warning("⚠️ Consider purchasing more credits")
        else:
            st.error("❌ Low credit balance")
    
    with balance_col2:
        st.markdown("**💡 Credit Usage:**")
        st.write("• Document Generation: 10 credits")
        st.write("• AI Editing/Modifications: 5 credits")
        st.write("• Document Regeneration: 10 credits")
    
    st.divider()
    
    # Purchase credits
    st.subheader("🛒 Purchase Credits")
    
    credit_packages = [
        {"credits": 50, "price": "$25", "value": "Starter Pack"},
        {"credits": 100, "price": "$45", "value": "Popular Choice", "savings": "Save $5"},
        {"credits": 250, "price": "$100", "value": "Professional", "savings": "Save $25"},
        {"credits": 500, "price": "$180", "value": "Enterprise", "savings": "Save $70"}
    ]
    
    package_cols = st.columns(len(credit_packages))
    
    for i, (col, package) in enumerate(zip(package_cols, credit_packages)):
        with col:
            with st.container():
                if package.get('savings'):
                    st.success(f"💎 {package['value']}")
                else:
                    st.info(f"📦 {package['value']}")
                
                st.markdown(f"**{package['credits']} Credits**")
                st.markdown(f"**{package['price']}**")
                
                if package.get('savings'):
                    st.markdown(f"*{package['savings']}*")
                
                if st.button(f"Purchase", key=f"buy_{i}", type="primary"):
                    # Mock purchase
                    coordinator['credits_balance'] += package['credits']
                    st.session_state.coordinator_profile = coordinator
                    st.success(f"✅ {package['credits']} credits added!")
                    st.balloons()
                    st.rerun()
    
    st.divider()
    
    # Usage history
    st.subheader("📊 Usage History")
    
    # Mock usage data
    usage_data = []
    recent_docs = st.session_state.get('recent_documents', [])
    
    for doc in recent_docs:
        usage_data.append({
            'date': doc.get('created_at', 'Unknown'),
            'action': 'Document Generation',
            'document': doc.get('document_name', 'Unknown'),
            'credits': doc.get('credits_used', 10)
        })
    
    if usage_data:
        for usage in reversed(usage_data[-10:]):  # Show last 10 transactions
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(usage['date'][:10])
            
            with col2:
                st.write(usage['action'])
            
            with col3:
                st.write(usage['document'])
            
            with col4:
                st.write(f"-{usage['credits']}")
    else:
        st.info("No usage history yet.")
    
    st.divider()
    
    # Account management
    st.subheader("⚙️ Account Settings")
    
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        if st.button("📧 Update Email Notifications"):
            st.info("Email notification settings would open here.")
    
    with settings_col2:
        if st.button("📄 Download Invoice"):
            st.info("Invoice download would be available here.")