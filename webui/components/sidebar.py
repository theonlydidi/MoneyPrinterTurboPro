import streamlit as st

def render_sidebar():
    """Render the main sidebar navigation"""
    
    with st.sidebar:
        st.title("🎬 MoneyPrinterTurboPro")
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### 🧭 Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("🎬 Video Generator", use_container_width=True, key="nav_video_generator"):
            st.session_state.current_page = "video_generator"
            st.rerun()
        
        if st.button("📋 Templates", use_container_width=True, key="nav_templates"):
            st.session_state.current_page = "templates"
            st.rerun()
        
        if st.button("📊 Analytics", use_container_width=True, key="nav_analytics"):
            st.session_state.current_page = "analytics"
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
            st.session_state.current_page = "settings"
            st.rerun()
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Videos", "1,247")
        with col2:
            st.metric("Templates", "23")
        
        st.markdown("---")
        
        # User info
        st.markdown("### 👤 User Info")
        st.info("**Demo User**")
        st.markdown("Premium Account")
        st.markdown("Member since Aug 2024")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        # Footer
        st.markdown("### 📱 Support")
        st.markdown("**Version:** 2.0.0")
        st.markdown("**Status:** 🟢 Online")
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
