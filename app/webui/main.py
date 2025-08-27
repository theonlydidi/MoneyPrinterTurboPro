"""
Streamlit WebUI application creation for MoneyPrinterTurboPro
"""

import streamlit as st
from loguru import logger

from ..core.config import settings


def create_webui_app():
    """Create and configure Streamlit WebUI application"""
    try:
        # Configure Streamlit page
        st.set_page_config(
            page_title="MoneyPrinterTurboPro",
            page_icon="🎬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main title
        st.title("🎬 MoneyPrinterTurboPro")
        st.markdown("**AI-Powered Video Generation Platform**")
        
        # Status information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", "🟢 Active")
        
        with col2:
            st.metric("Version", "2.0.0")
        
        with col3:
            st.metric("Mode", "Development" if settings.development.debug else "Production")
        
        # Feature overview
        st.subheader("🚀 Available Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - **🎬 Video Generation** - AI-powered video creation
            - **🤖 AI Models** - Multiple LLM providers
            - **🎨 Templates** - Professional video styles
            - **📊 Analytics** - Performance insights
            """)
        
        with col2:
            st.markdown("""
            - **🔌 Plugins** - Extensible architecture
            - **💾 Storage** - Multi-cloud support
            - **📱 WebUI** - Modern interface
            - **🔒 Security** - Authentication & rate limiting
            """)
        
        # Quick start
        st.subheader("🚀 Quick Start")
        
        if st.button("Generate Sample Video", type="primary"):
            st.info("🎬 Video generation feature is available in the Video Generator page!")
            st.success("✅ Your MoneyPrinterTurboPro is ready to use!")
        
        logger.info("✅ Streamlit WebUI application created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ WebUI application creation failed: {e}")
        return False
