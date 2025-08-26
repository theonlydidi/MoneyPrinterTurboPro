import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import requests

# Import page modules
from pages.dashboard import render_dashboard
from pages.video_generator import render_video_generator
from pages.templates import render_templates
from pages.analytics import render_analytics
from pages.settings import render_settings

# Import components
from components.sidebar import render_sidebar
from components.auth import check_authentication

# Import utilities
from utils.session import init_session_state
from utils.config import get_config

def main():
    # Page configuration
    st.set_page_config(
        page_title="MoneyPrinterTurboPro - AI Video Generation Platform",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not check_authentication():
        render_login_page()
        return
    
    # Main application
    render_main_app()

def render_login_page():
    """Render the login page for unauthenticated users"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🎬 MoneyPrinterTurboPro</h1>
        <h3>AI-Powered Video Generation Platform</h3>
        <p>Create professional videos with artificial intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Authentication Required")
        
        # Demo login (in production, this would connect to real auth)
        if st.button("🚀 Demo Login", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user = {
                "username": "demo_user",
                "email": "demo@moneyprinterturbopro.com",
                "role": "premium"
            }
            st.rerun()
        
        st.info("💡 **Demo Mode**: Click 'Demo Login' to explore the platform")
        
        # Feature highlights
        st.markdown("### ✨ Platform Features")
        features = [
            "🎬 **AI Video Generation** - Create videos from text descriptions",
            "🤖 **Multi-Model AI** - GPT-4, Claude, Gemini, and more",
            "🗣️ **Professional Voice Synthesis** - Multiple voice providers",
            "🎵 **AI Music Generation** - Custom background music",
            "🎨 **Advanced Effects** - Professional video editing",
            "📊 **Analytics Dashboard** - Performance insights",
            "⚡ **Real-time Processing** - Live generation tracking",
            "🌐 **Multi-language Support** - Global accessibility"
        ]
        
        for feature in features:
            st.markdown(f"• {feature}")

def render_main_app():
    """Render the main application for authenticated users"""
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    main_container = st.container()
    
    with main_container:
        # Navigation based on sidebar selection
        if st.session_state.get("current_page", "dashboard") == "dashboard":
            render_dashboard()
        elif st.session_state.get("current_page") == "video_generator":
            render_video_generator()
        elif st.session_state.get("current_page") == "templates":
            render_templates()
        elif st.session_state.get("current_page") == "analytics":
            render_analytics()
        elif st.session_state.get("current_page") == "settings":
            render_settings()
        else:
            render_dashboard()

def render_welcome_banner():
    """Render a welcome banner for new users"""
    if st.session_state.get("show_welcome", True):
        with st.container():
            st.markdown("""
            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h2>🎉 Welcome to MoneyPrinterTurboPro!</h2>
                <p>You're now using the most advanced AI video generation platform. 
                Start creating professional videos in minutes!</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🚀 Create Your First Video", use_container_width=True):
                    st.session_state.current_page = "video_generator"
                    st.rerun()
            
            with col2:
                if st.button("📊 Explore Dashboard", use_container_width=True):
                    st.session_state.current_page = "dashboard"
                    st.rerun()
            
            with col3:
                if st.button("❌ Dismiss", use_container_width=True):
                    st.session_state.show_welcome = False
                    st.rerun()

def render_quick_stats():
    """Render quick statistics at the top of the main area"""
    if st.session_state.get("current_page") == "dashboard":
        return  # Don't show on dashboard page
    
    st.markdown("### 📊 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎬 Videos Today",
            value="12",
            delta="+3"
        )
    
    with col2:
        st.metric(
            label="⏱️ Avg. Time",
            value="3.2 min",
            delta="-0.5 min"
        )
    
    with col3:
        st.metric(
            label="💰 Today's Cost",
            value="$4.85",
            delta="+$1.20"
        )
    
    with col4:
        st.metric(
            label="⭐ Quality Score",
            value="4.8/5.0",
            delta="+0.1"
        )

def render_feature_highlights():
    """Render feature highlights for the current page"""
    current_page = st.session_state.get("current_page", "dashboard")
    
    if current_page == "video_generator":
        st.info("💡 **Pro Tip**: Use specific, descriptive topics for better AI-generated content. Try 'How to make perfect coffee in 5 minutes' instead of just 'coffee'.")
    
    elif current_page == "templates":
        st.info("💡 **Pro Tip**: Save your favorite video configurations as templates to speed up future video creation.")
    
    elif current_page == "analytics":
        st.info("💡 **Pro Tip**: Monitor your video generation patterns to optimize costs and improve quality over time.")
    
    elif current_page == "settings":
        st.info("💡 **Pro Tip**: Configure your preferred AI models and voice settings for consistent video generation.")

def render_footer():
    """Render the application footer"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem;">
            <p>🎬 <strong>MoneyPrinterTurboPro</strong> - AI-Powered Video Generation Platform</p>
            <p>Built with ❤️ using Streamlit, Plotly, and advanced AI technologies</p>
            <p>© 2024 MoneyPrinterTurboPro. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)

# Enhanced main function with error handling
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"🚨 An error occurred: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")
        
        # Show error details in development
        if st.session_state.get("debug_mode", False):
            st.exception(e)
