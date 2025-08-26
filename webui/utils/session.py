import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
