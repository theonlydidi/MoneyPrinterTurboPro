import streamlit as st
import json
from datetime import datetime
import time

def render_settings():
    st.header("⚙️ Settings & Configuration")
    st.markdown("Customize your MoneyPrinterTurboPro experience and manage preferences")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🎨 Appearance", "🤖 AI Settings", "🔒 Security"])
    
    with tab1:
        render_profile_settings()
    
    with tab2:
        render_appearance_settings()
    
    with tab3:
        render_ai_settings()
    
    with tab4:
        render_security_settings()

def render_profile_settings():
    st.subheader("👤 User Profile Settings")
    
    # User profile information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Personal Information")
        
        username = st.text_input(
            "👤 Username",
            value="demo_user",
            help="Your unique username for the platform"
        )
        
        email = st.text_input(
            "📧 Email Address",
            value="demo@moneyprinterturbopro.com",
            help="Your primary email address"
        )
        
        full_name = st.text_input(
            "📛 Full Name",
            value="Demo User",
            help="Your full name as it should appear"
        )
        
        company = st.text_input(
            "🏢 Company/Organization",
            value="Demo Company",
            help="Your company or organization name"
        )
        
        role = st.text_input(
            "💼 Job Title/Role",
            value="Content Creator",
            help="Your professional role or title"
        )
    
    with col2:
        st.markdown("### 📊 Account Status")
        
        st.info("**Account Type**: Premium")
        st.metric("Member Since", "August 2024")
        st.metric("Videos Generated", "1,247")
        st.metric("Storage Used", "2.3 GB")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Stats", use_container_width=True):
            st.success("Account statistics refreshed!")
    
    # Preferences
    st.markdown("### ⚙️ Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_language = st.selectbox(
            "🌍 Default Language",
            ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Arabic"],
            help="Your preferred language for the interface"
        )
        
        timezone = st.selectbox(
            "⏰ Timezone",
            ["UTC", "EST", "PST", "GMT", "CET", "JST", "AEST"],
            help="Your local timezone"
        )
        
        notification_email = st.checkbox(
            "📧 Email Notifications",
            value=True,
            help="Receive email notifications for video completion"
        )
        
        notification_push = st.checkbox(
            "🔔 Push Notifications",
            value=True,
            help="Receive push notifications in the browser"
        )
    
    with col2:
        auto_save = st.checkbox(
            "💾 Auto-save Drafts",
            value=True,
            help="Automatically save video generation drafts"
        )
        
        quality_preference = st.selectbox(
            "🎨 Default Quality",
            ["720p", "1080p", "1440p", "4K"],
            index=1,
            help="Default video quality for new generations"
        )
        
        storage_cleanup = st.checkbox(
            "🧹 Auto-cleanup",
            value=True,
            help="Automatically clean up old temporary files"
        )
    
    # Save profile changes
    if st.button("💾 Save Profile Changes", type="primary", use_container_width=True):
        with st.spinner("Saving changes..."):
            time.sleep(1)
            st.success("✅ Profile settings saved successfully!")

def render_appearance_settings():
    st.subheader("🎨 Appearance & Theme")
    
    # Theme selection
    st.markdown("### 🎨 Theme Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme_mode = st.selectbox(
            "🌓 Theme Mode",
            ["Light", "Dark", "Auto"],
            help="Choose your preferred theme mode"
        )
        
        primary_color = st.color_picker(
            "🎨 Primary Color",
            value="#667eea",
            help="Main accent color for the interface"
        )
        
        accent_color = st.color_picker(
            "✨ Accent Color",
            value="#764ba2",
            help="Secondary accent color"
        )
    
    with col2:
        font_size = st.selectbox(
            "📝 Font Size",
            ["Small", "Medium", "Large", "Extra Large"],
            index=1,
            help="Text size preference"
        )
        
        font_family = st.selectbox(
            "🔤 Font Family",
            ["Sans Serif", "Serif", "Monospace", "Cursive"],
            help="Font style preference"
        )
    
    # Layout preferences
    st.markdown("### 📱 Layout Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sidebar_position = st.selectbox(
            "📍 Sidebar Position",
            ["Left", "Right"],
            help="Choose sidebar placement"
        )
        
        sidebar_width = st.slider(
            "📏 Sidebar Width",
            min_value=200,
            max_value=400,
            value=300,
            step=50,
            help="Adjust sidebar width in pixels"
        )
        
        compact_mode = st.checkbox(
            "📦 Compact Mode",
            value=False,
            help="Use compact layout for more content"
        )
    
    with col2:
        show_animations = st.checkbox(
            "✨ Show Animations",
            value=True,
            help="Enable interface animations"
        )
        
        show_tooltips = st.checkbox(
            "💡 Show Tooltips",
            value=True,
            help="Display helpful tooltips"
        )
        
        auto_expand = st.checkbox(
            "📖 Auto-expand Sections",
            value=False,
            help="Automatically expand all sections"
        )
    
    # Preview
    st.markdown("### 👀 Theme Preview")
    
    # Create a preview box with the selected colors
    preview_html = f"""
    <div style="
        background: linear-gradient(135deg, {primary_color}, {accent_color});
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    ">
        <h3>🎨 Theme Preview</h3>
        <p>This is how your selected colors will look in the interface</p>
        <div style="
            background: rgba(255,255,255,0.2);
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        ">
            <strong>Primary:</strong> {primary_color} | <strong>Accent:</strong> {accent_color}
        </div>
    </div>
    """
    
    st.markdown(preview_html, unsafe_allow_html=True)
    
    # Save appearance changes
    if st.button("💾 Save Appearance Settings", type="primary", use_container_width=True):
        with st.spinner("Saving appearance settings..."):
            time.sleep(1)
            st.success("✅ Appearance settings saved successfully!")

def render_ai_settings():
    st.subheader("🤖 AI Model Configuration")
    
    # Default AI settings
    st.markdown("### 🧠 Default AI Models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_llm = st.selectbox(
            "🧠 Default LLM Provider",
            ["OpenAI GPT-4", "Anthropic Claude", "Google Gemini", "Qwen", "Moonshot", "Ollama"],
            help="Default AI model for script generation"
        )
        
        default_voice = st.selectbox(
            "🗣️ Default Voice Provider",
            ["Edge TTS", "Azure Speech", "ElevenLabs", "Google TTS", "Coqui TTS"],
            help="Default text-to-speech service"
        )
        
        default_music = st.selectbox(
            "🎵 Default Music Provider",
            ["AI Generated", "Stock Music", "Custom Upload", "No Music"],
            help="Default background music source"
        )
    
    with col2:
        default_effects = st.selectbox(
            "🎨 Default Effects Style",
            ["Professional", "Creative", "Minimal", "Cinematic", "Vintage", "Modern"],
            help="Default video effects style"
        )
        
        default_subtitles = st.selectbox(
            "📝 Default Subtitle Style",
            ["Modern", "Classic", "Bold", "Elegant", "Playful", "Corporate"],
            help="Default subtitle appearance"
        )
    
    # AI behavior settings
    st.markdown("### ⚙️ AI Behavior Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        creativity_level = st.slider(
            "🎨 Creativity Level",
            min_value=1,
            max_value=10,
            value=7,
            help="How creative should AI-generated content be?"
        )
        
        quality_priority = st.selectbox(
            "🎯 Quality Priority",
            ["Speed", "Balanced", "Quality", "Maximum Quality"],
            index=1,
            help="Balance between speed and quality"
        )
        
        auto_retry = st.checkbox(
            "🔄 Auto-retry Failed Generations",
            value=True,
            help="Automatically retry failed AI generations"
        )
    
    with col2:
        fallback_models = st.multiselect(
            "🔄 Fallback Models",
            ["OpenAI GPT-4", "Anthropic Claude", "Google Gemini", "Qwen", "Moonshot", "Ollama"],
            default=["Anthropic Claude", "Google Gemini"],
            help="Models to try if the primary model fails"
        )
        
        cost_optimization = st.checkbox(
            "💰 Cost Optimization",
            value=True,
            help="Automatically select cost-efficient models when possible"
        )
        
        content_filtering = st.checkbox(
            "🛡️ Content Filtering",
            value=True,
            help="Apply content safety filters to AI generations"
        )
    
    # Advanced AI settings
    st.markdown("### 🔬 Advanced AI Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_tokens = st.slider(
            "📝 Max Script Length",
            min_value=100,
            max_value=2000,
            value=500,
            step=100,
            help="Maximum tokens for AI script generation"
        )
        
        temperature = st.slider(
            "🌡️ AI Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in AI responses (0=deterministic, 2=creative)"
        )
        
        top_p = st.slider(
            "🎯 Top P Sampling",
            min_value=0.1,
            max_value=1.0,
            value=0.9,
            step=0.1,
            help="Controls diversity in AI responses"
        )
    
    with col2:
        frequency_penalty = st.slider(
            "🔄 Frequency Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Penalize repetitive content"
        )
        
        presence_penalty = st.slider(
            "📍 Presence Penalty",
            min_value=-2.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Penalize new topics"
        )
    
    # Save AI settings
    if st.button("💾 Save AI Settings", type="primary", use_container_width=True):
        with st.spinner("Saving AI settings..."):
            time.sleep(1)
            st.success("✅ AI settings saved successfully!")

def render_security_settings():
    st.subheader("🔒 Security & Privacy")
    
    # Account security
    st.markdown("### 🛡️ Account Security")
    
    col1, col2 = st.columns(2)
    
    with col1:
        two_factor_auth = st.checkbox(
            "🔐 Two-Factor Authentication",
            value=False,
            help="Enable 2FA for additional security"
        )
        
        session_timeout = st.selectbox(
            "⏰ Session Timeout",
            ["15 minutes", "30 minutes", "1 hour", "4 hours", "24 hours", "Never"],
            index=2,
            help="Auto-logout after inactivity"
        )
        
        login_notifications = st.checkbox(
            "🔔 Login Notifications",
            value=True,
            help="Notify on new login attempts"
        )
    
    with col2:
        password_strength = st.selectbox(
            "🔑 Password Requirements",
            ["Basic", "Strong", "Very Strong", "Maximum"],
            index=1,
            help="Minimum password strength requirements"
        )
        
        failed_login_limit = st.slider(
            "🚫 Failed Login Limit",
            min_value=3,
            max_value=10,
            value=5,
            help="Account lockout after failed attempts"
        )
    
    # Privacy settings
    st.markdown("### 🔒 Privacy Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_collection = st.checkbox(
            "📊 Usage Analytics",
            value=True,
            help="Allow collection of usage analytics"
        )
        
        personalized_content = st.checkbox(
            "🎯 Personalized Content",
            value=True,
            help="Use your data to personalize content"
        )
        
        third_party_sharing = st.checkbox(
            "🤝 Third-party Sharing",
            value=False,
            help="Allow sharing data with third parties"
        )
    
    with col2:
        data_retention = st.selectbox(
            "🗄️ Data Retention",
            ["30 days", "90 days", "6 months", "1 year", "Forever"],
            index=2,
            help="How long to keep your data"
        )
        
        export_data = st.checkbox(
            "📥 Data Export",
            value=True,
            help="Allow you to export your data"
        )
    
    # API and integration security
    st.markdown("### 🔌 API & Integration Security")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_rate_limit = st.slider(
            "🚦 API Rate Limit",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Maximum API requests per hour"
        )
        
        webhook_security = st.checkbox(
            "🔗 Webhook Security",
            value=True,
            help="Validate webhook signatures"
        )
    
    with col2:
        ip_whitelist = st.text_area(
            "🌐 IP Whitelist",
            placeholder="Enter allowed IP addresses (one per line)",
            help="Restrict access to specific IP addresses"
        )
        
        api_key_rotation = st.selectbox(
            "🔄 API Key Rotation",
            ["30 days", "90 days", "6 months", "1 year", "Manual"],
            index=1,
            help="How often to rotate API keys"
        )
    
    # Security actions
    st.markdown("### ⚡ Security Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔑 Change Password", use_container_width=True):
            st.info("Password change functionality would be implemented here")
    
    with col2:
        if st.button("📱 Setup 2FA", use_container_width=True):
            st.info("Two-factor authentication setup would be implemented here")
    
    with col3:
        if st.button("🚪 Logout All Sessions", use_container_width=True):
            st.success("All sessions logged out successfully!")
    
    # Save security settings
    if st.button("💾 Save Security Settings", type="primary", use_container_width=True):
        with st.spinner("Saving security settings..."):
            time.sleep(1)
            st.success("✅ Security settings saved successfully!")

# Main function
if __name__ == "__main__":
    render_settings()
