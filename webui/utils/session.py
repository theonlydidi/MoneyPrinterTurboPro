import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False

def get_session_value(key, default=None):
    """Get a value from session state"""
    return st.session_state.get(key, default)

def set_session_value(key, value):
    """Set a value in session state"""
    st.session_state[key] = value

def update_video_generation_status(video_id, status, progress=None):
    """Update video generation status"""
    if 'video_generation_status' not in st.session_state:
        st.session_state.video_generation_status = {}
    
    st.session_state.video_generation_status[video_id] = {
        'status': status,
        'progress': progress,
        'timestamp': st.session_state.get('timestamp', 0)
    }

def get_video_generation_status(video_id):
    """Get video generation status"""
    if 'video_generation_status' not in st.session_state:
        return None
    return st.session_state.video_generation_status.get(video_id)

def set_form_data(form_type, data):
    """Store form data in session"""
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    st.session_state.form_data[form_type] = data

def get_form_data(form_type):
    """Retrieve form data from session"""
    if 'form_data' not in st.session_state:
        return None
    return st.session_state.form_data.get(form_type)

def clear_form_data(form_type=None):
    """Clear form data from session"""
    if form_type is None:
        if 'form_data' in st.session_state:
            del st.session_state.form_data
    else:
        if 'form_data' in st.session_state and form_type in st.session_state.form_data:
            del st.session_state.form_data[form_type]
