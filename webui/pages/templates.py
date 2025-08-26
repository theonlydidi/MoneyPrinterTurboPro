import streamlit as st
import pandas as pd
from datetime import datetime
import json
import time

def render_templates():
    st.header("📋 Video Templates")
    st.markdown("Manage and use video generation templates for consistent results")
    
    # Create tabs for different template views
    tab1, tab2, tab3 = st.tabs(["🎯 My Templates", "📚 Preset Templates", "➕ Create Template"])
    
    with tab1:
        render_my_templates()
    
    with tab2:
        render_preset_templates()
    
    with tab3:
        render_create_template()

def render_my_templates():
    st.subheader("🎯 My Custom Templates")
    
    # Sample user templates
    user_templates = [
        {
            "name": "Professional Business",
            "style": "Corporate",
            "voice": "Professional Male",
            "music": "Corporate Background",
            "resolution": "1080p",
            "duration": "60s",
            "created": "2024-08-26",
            "usage_count": 15
        },
        {
            "name": "Educational Tutorial",
            "style": "Educational",
            "voice": "Professional Female",
            "music": "Calm Background",
            "resolution": "1080p",
            "duration": "120s",
            "created": "2024-08-25",
            "usage_count": 8
        },
        {
            "name": "Social Media Short",
            "style": "Casual",
            "voice": "Casual Male",
            "music": "Upbeat",
            "resolution": "720p",
            "duration": "30s",
            "created": "2024-08-24",
            "usage_count": 23
        }
    ]
    
    # Template management options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📋 Your Templates")
        
        # Display templates in a table
        df = pd.DataFrame(user_templates)
        st.dataframe(df, use_container_width=True)
    
    with col2:
        st.markdown("### ⚙️ Actions")
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.success("Templates refreshed!")
        
        if st.button("📥 Export", use_container_width=True):
            st.info("Exporting templates...")
        
        st.markdown("---")
        
        st.markdown("### 📊 Stats")
        st.metric("Total Templates", len(user_templates))
        st.metric("Most Used", "Social Media Short")
        st.metric("Total Usage", "46 videos")

def render_preset_templates():
    st.subheader("📚 Preset Templates")
    
    # Preset template categories
    categories = ["Business", "Education", "Entertainment", "Marketing", "Social Media"]
    
    selected_category = st.selectbox("🎯 Select Category", categories)
    
    # Sample preset templates based on category
    preset_templates = {
        "Business": [
            {"name": "Corporate Presentation", "description": "Professional business presentations", "style": "Corporate"},
            {"name": "Product Demo", "description": "Product demonstration videos", "style": "Professional"},
            {"name": "Team Introduction", "description": "Company team introductions", "style": "Corporate"}
        ],
        "Education": [
            {"name": "Lecture Recording", "description": "Academic lecture recordings", "style": "Educational"},
            {"name": "Tutorial Guide", "description": "Step-by-step tutorials", "style": "Educational"},
            {"name": "Concept Explanation", "description": "Complex concept explanations", "style": "Educational"}
        ],
        "Entertainment": [
            {"name": "Story Time", "description": "Narrative storytelling", "style": "Entertainment"},
            {"name": "Comedy Sketch", "description": "Humorous content", "style": "Entertainment"},
            {"name": "Music Video", "description": "Music-focused content", "style": "Creative"}
        ],
        "Marketing": [
            {"name": "Product Launch", "description": "New product announcements", "style": "Marketing"},
            {"name": "Customer Testimonial", "description": "Customer success stories", "style": "Marketing"},
            {"name": "Brand Story", "description": "Company brand narratives", "style": "Marketing"}
        ],
        "Social Media": [
            {"name": "Instagram Story", "description": "Vertical social media content", "style": "Social"},
            {"name": "TikTok Style", "description": "Short-form engaging content", "style": "Social"},
            {"name": "LinkedIn Post", "description": "Professional social content", "style": "Professional"}
        ]
    }
    
    # Display templates for selected category
    templates = preset_templates.get(selected_category, [])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📚 {selected_category} Templates")
        
        for i, template in enumerate(templates):
            with st.expander(f"🎯 {template['name']}"):
                st.markdown(f"**Description:** {template['description']}")
                st.markdown(f"**Style:** {template['style']}")
                
                col1a, col1b = st.columns(2)
                with col1a:
                    if st.button(f"🚀 Use Template", key=f"use_{i}"):
                        st.success(f"Using template: {template['name']}")
                with col1b:
                    if st.button(f"💾 Save to My Templates", key=f"save_{i}"):
                        st.success(f"Saved: {template['name']}")
    
    with col2:
        st.markdown("### 💡 Tips")
        tips = [
            "🎯 **Choose Wisely**: Select templates that match your content goals",
            "🔄 **Customize**: Modify preset templates to fit your needs",
            "💾 **Save Favorites**: Save frequently used templates",
            "📊 **Track Usage**: Monitor which templates work best"
        ]
        
        for tip in tips:
            st.markdown(tip)

def render_create_template():
    st.subheader("➕ Create New Template")
    
    # Template creation form
    col1, col2 = st.columns(2)
    
    with col1:
        template_name = st.text_input(
            "📝 Template Name",
            placeholder="Enter a descriptive name for your template",
            help="Choose a name that clearly describes the template's purpose"
        )
        
        template_description = st.text_area(
            "📖 Description",
            placeholder="Describe what this template is for and when to use it",
            height=100,
            help="Provide a clear description of the template's use case"
        )
        
        template_style = st.selectbox(
            "🎨 Video Style",
            ["Professional", "Casual", "Educational", "Entertainment", "Corporate", "Creative"],
            help="Choose the overall style and tone"
        )
        
        template_duration = st.slider(
            "⏱️ Target Duration (seconds)",
            min_value=15,
            max_value=300,
            value=60,
            step=15,
            help="How long should videos using this template be?"
        )
    
    with col2:
        voice_preset = st.selectbox(
            "🗣️ Voice Character",
            ["Professional Male", "Professional Female", "Casual Male", "Casual Female", "Narrator", "News Anchor"],
            help="Default voice for this template"
        )
        
        music_mood = st.selectbox(
            "🎶 Music Mood",
            ["Upbeat", "Calm", "Energetic", "Professional", "Creative", "Dramatic"],
            help="Default background music mood"
        )
        
        video_resolution = st.selectbox(
            "📺 Resolution",
            ["720p", "1080p", "1440p", "4K"],
            index=1,
            help="Default video output resolution"
        )
        
        auto_subtitles = st.checkbox("📝 Auto-generate subtitles", value=True)
        watermark = st.checkbox("💧 Add watermark", value=False)
    
    # Advanced settings
    st.markdown("### ⚙️ Advanced Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        transition_type = st.selectbox(
            "🔄 Transitions",
            ["Fade", "Slide", "Zoom", "Dissolve", "Wipe", "None"],
            help="Default transition effects"
        )
        
        color_grade = st.selectbox(
            "🎨 Color Grade",
            ["Natural", "Warm", "Cool", "Cinematic", "Vintage", "Modern"],
            help="Default color grading style"
        )
    
    with col2:
        text_style = st.selectbox(
            "📝 Text Style",
            ["Modern", "Classic", "Bold", "Elegant", "Playful", "Corporate"],
            help="Default subtitle and text appearance"
        )
        
        animation_style = st.selectbox(
            "✨ Animation",
            ["Smooth", "Bouncy", "Sharp", "Gentle", "Dynamic", "Minimal"],
            help="Default animation style"
        )
    
    with col3:
        optimize_for_platform = st.selectbox(
            "📱 Platform Optimization",
            ["YouTube", "Instagram", "TikTok", "LinkedIn", "Facebook", "Twitter", "Universal"],
            help="Optimize for specific platform"
        )
        
        compression_level = st.selectbox(
            "🗜️ Compression",
            ["High Quality", "Balanced", "Small File Size"],
            index=1,
            help="Video compression level"
        )
    
    # Template tags
    template_tags = st.text_input(
        "🏷️ Tags",
        placeholder="Enter tags separated by commas (e.g., business, professional, corporate)",
        help="Add tags to help organize and find your templates"
    )
    
    # Create template button
    if st.button("🚀 Create Template", type="primary", use_container_width=True):
        if template_name and template_description:
            # Simulate template creation
            with st.spinner("Creating template..."):
                time.sleep(2)
                
                # Show success message
                st.success("🎉 Template created successfully!")
                
                # Show template summary
                st.markdown("### 📋 Template Summary")
                template_summary = {
                    "Name": template_name,
                    "Description": template_description,
                    "Style": template_style,
                    "Duration": f"{template_duration}s",
                    "Voice": voice_preset,
                    "Music": music_mood,
                    "Resolution": video_resolution,
                    "Tags": template_tags
                }
                
                for key, value in template_summary.items():
                    st.markdown(f"**{key}:** {value}")
                
                # Download template config
                template_config = {
                    "template_name": template_name,
                    "template_description": template_description,
                    "template_style": template_style,
                    "template_duration": template_duration,
                    "voice_preset": voice_preset,
                    "music_mood": music_mood,
                    "video_resolution": video_resolution,
                    "auto_subtitles": auto_subtitles,
                    "watermark": watermark,
                    "transition_type": transition_type,
                    "color_grade": color_grade,
                    "text_style": text_style,
                    "animation_style": animation_style,
                    "optimize_for_platform": optimize_for_platform,
                    "compression_level": compression_level,
                    "template_tags": template_tags,
                    "created_date": datetime.now().isoformat()
                }
                
                st.download_button(
                    label="📥 Download Template Config",
                    data=json.dumps(template_config, indent=2),
                    file_name=f"template_{template_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.error("Please provide a template name and description!")

# Main function
if __name__ == "__main__":
    render_templates()
