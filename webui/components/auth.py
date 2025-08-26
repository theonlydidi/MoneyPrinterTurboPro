import streamlit as st

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    return st.session_state.authenticated

def login_user():
    """Set user as authenticated"""
    st.session_state.authenticated = True

def logout_user():
    """Set user as logged out"""
    st.session_state.authenticated = False
