# frontend/components/credit_display.py
import streamlit as st
from typing import Dict, Any

def display_credit_status(coordinator: Dict[str, Any]):
    """Display coordinator's credit status"""
    
    credits = coordinator.get('credits_balance', 0)
    
    # Color coding based on credit level
    if credits > 50:
        st.success(f"💰 Credits: {credits}")
    elif credits > 20:
        st.warning(f"⚠️ Credits: {credits}")
    else:
        st.error(f"❌ Credits: {credits} - Please purchase more")
    
    return credits

def show_credit_usage_modal(action: str, credits_required: int, current_balance: int):
    """Show credit usage confirmation modal"""
    
    if current_balance < credits_required:
        st.error(f"❌ Insufficient credits for {action}")
        st.write(f"Required: {credits_required} credits")
        st.write(f"Available: {current_balance} credits") 
        
        if st.button("💳 Purchase Credits"):
            st.session_state.current_page = 'billing'
            st.rerun()
        
        return False
    else:
        st.info(f"💰 {action} will use {credits_required} credits")
        st.write(f"Remaining after: {current_balance - credits_required} credits")
        return True