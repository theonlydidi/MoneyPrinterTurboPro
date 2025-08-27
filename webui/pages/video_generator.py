import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import json
from datetime import datetime
import os
import tempfile

# Try to import OpenCV with fallback
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    st.error("⚠️ OpenCV not available. Please install with: pip install opencv-python")
    st.info("Video generation will be limited without OpenCV")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    st.warning("PIL not available. Some features may be limited.")

def render_video_generator():
    st.header("🎬 Advanced Video Generator")
    st.markdown("Create professional AI-powered videos with advanced customization")
    
    # Check if OpenCV is available
    if not OPENCV_AVAILABLE:
        st.error("🚨 OpenCV is required for video generation!")
        st.info("Please install OpenCV by running: `pip install opencv-python`")
        st.info("Then restart the WebUI application.")
        return
    
    # Create tabs for different generation modes
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Quick Generate", "⚙️ Advanced Settings", "📊 Batch Processing", "📚 Video History"])
    
    with tab1:
        render_quick_generate()
    
    with tab2:
        render_advanced_settings()
    
    with tab3:
        render_batch_processing()
    
    with tab4:
        show_video_history()

def render_quick_generate():
    st.subheader("Quick Video Generation")
    
    # Video Topic & Script
    col1, col2 = st.columns([2, 1])
    
    with col1:
        video_topic = st.text_input(
            "🎯 Video Topic",
            placeholder="Enter your video topic (e.g., 'How to make perfect coffee')",
            help="Describe what your video will be about"
        )
        
        video_style = st.selectbox(
            "🎨 Video Style",
            ["Professional", "Creative", "Educational", "Entertainment", "Corporate"],
            help="Choose the overall style and tone"
        )
        
        video_length = st.slider(
            "⏱️ Target Duration (seconds)",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
            help="How long should the video be?"
        )
        
        # AI Content Generation
        if st.checkbox("🤖 Use AI to generate content", value=True, help="Let AI create a professional script for your video"):
            target_audience = st.selectbox(
                "👥 Target Audience",
                ["General", "Business", "Students", "Professionals", "Creators", "Beginners"],
                help="Who is this video for?"
            )
            
            language = st.selectbox(
                "🌍 Language",
                ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
                help="What language should the content be in?"
            )
            
            # Monetization & Success Optimization
            st.subheader("💰 Monetization & Success Optimization")
            
            monetization_focus = st.selectbox(
                "🎯 Primary Monetization Focus",
                ["engagement", "affiliate", "ads", "sponsorships"],
                help="What's your main goal for this video?"
            )
            
            platform = st.selectbox(
                "📱 Target Platform",
                ["youtube", "tiktok", "instagram", "facebook"],
                help="Which platform are you optimizing for?"
            )
            
            # Show platform-specific insights
            if st.checkbox("📊 Show Success Insights", value=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**{platform.upper()} Success Metrics**")
                    if platform == "youtube":
                        st.metric("Viral Threshold", "100K+ views in 24h")
                        st.metric("Monetization", "1K+ subscribers")
                        st.metric("Optimal Length", "8-15 minutes")
                    elif platform == "tiktok":
                        st.metric("Viral Threshold", "500K+ views in 24h")
                        st.metric("Monetization", "10K+ followers")
                        st.metric("Optimal Length", "15-60 seconds")
                    elif platform == "instagram":
                        st.metric("Viral Threshold", "200K+ views in 24h")
                        st.metric("Monetization", "5K+ followers")
                        st.metric("Optimal Length", "15-90 seconds")
                    else:  # facebook
                        st.metric("Viral Threshold", "150K+ views in 24h")
                        st.metric("Monetization", "3K+ followers")
                        st.metric("Optimal Length", "1-5 minutes")
                
                with col2:
                    st.info(f"**{platform.upper()} Algorithm Favorites**")
                    if platform == "youtube":
                        st.write("• High retention (70%+ first 30s)")
                        st.write("• CTR above 8%")
                        st.write("• Engagement within 1 hour")
                    elif platform == "tiktok":
                        st.write("• 90%+ completion rate")
                        st.write("• Engagement within 3 hours")
                        st.write("• Shares over likes")
                    elif platform == "instagram":
                        st.write("• 5%+ engagement rate")
                        st.write("• Consistent posting")
                        st.write("• Trending hashtags")
                    else:  # facebook
                        st.write("• 3%+ engagement rate")
                        st.write("• Live content")
                        st.write("• Group participation")
    
    with col2:
        st.info("**AI-Powered Video Generation**")
        st.metric("Estimated Cost", "$0.00 (Local)")
        st.metric("Processing Time", "15-45 seconds")
        
        if st.button("🚀 Generate AI Video", type="primary", use_container_width=True):
            if video_topic:
                with st.spinner("🤖 AI is generating your video content..."):
                    try:
                        # Import AI content generator from local utils
                        try:
                            from ..utils.ai_generator import get_ai_generator
                        except ImportError:
                            # Fallback import path for Streamlit
                            import sys
                            import os
                            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
                            from ai_generator import get_ai_generator
                        
                        # Generate AI script
                        ai_gen = get_ai_generator()
                        script = ai_gen.generate_video_script(
                            topic=video_topic,
                            style=video_style,
                            duration=video_length,
                            target_audience=target_audience if 'target_audience' in locals() else "General",
                            language=language if 'language' in locals() else "English",
                            monetization_focus=monetization_focus if 'monetization_focus' in locals() else "engagement",
                            platform=platform if 'platform' in locals() else "youtube"
                        )
                        
                        # Store script in session state
                        st.session_state.ai_script = script
                        
                        st.success("✅ AI content generated successfully!")
                        
                        # Show script preview
                        with st.expander("📝 AI-Generated Script Preview", expanded=True):
                            st.json(script)
                        
                        # Show Success Insights & Market Analysis
                        with st.expander("📊 Success Insights & Market Analysis", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("🎯 Success Strategy")
                                if 'monetization_focus' in locals() and 'platform' in locals():
                                    st.info(f"**Monetization Focus:** {monetization_focus.title()}")
                                    st.info(f"**Target Platform:** {platform.title()}")
                                    
                                    # Show platform-specific success tips
                                    if platform == "youtube":
                                        st.success("**YouTube Success Tips:**")
                                        st.write("• Hook viewers in first 10 seconds")
                                        st.write("• Use trending topics and keywords")
                                        st.write("• Create custom thumbnails with high contrast")
                                        st.write("• Post Tuesday-Thursday 2-4 PM EST")
                                        st.write("• Use YouTube Shorts for discoverability")
                                    elif platform == "tiktok":
                                        st.success("**TikTok Success Tips:**")
                                        st.write("• Use trending sounds and music")
                                        st.write("• Participate in hashtag challenges")
                                        st.write("• Create content that encourages duets")
                                        st.write("• Post 1-3 times per day consistently")
                                        st.write("• Go live regularly for engagement")
                                    elif platform == "instagram":
                                        st.success("**Instagram Success Tips:**")
                                        st.write("• Use Reels for maximum reach")
                                        st.write("• Post stories daily with interactive elements")
                                        st.write("• Use trending hashtags and music")
                                        st.write("• Post at optimal times (8-10 AM, 2-4 PM, 7-9 PM EST)")
                                        st.write("• Collaborate with other creators")
                                    else:  # facebook
                                        st.success("**Facebook Success Tips:**")
                                        st.write("• Use video content over text posts")
                                        st.write("• Go live regularly for real-time engagement")
                                        st.write("• Create and engage in groups")
                                        st.write("• Post at optimal times (9-11 AM, 1-3 PM, 7-9 PM EST)")
                                        st.write("• Create shareable content")
                            
                            with col2:
                                st.subheader("📈 Market Trends")
                                if 'platform' in locals():
                                    if platform == "youtube":
                                        st.info("**Current YouTube Trends:**")
                                        st.write("• Shorts format (60s vertical) - 40% higher engagement")
                                        st.write("• Story-driven content - 3x more retention")
                                        st.write("• Interactive elements - 2x more comments")
                                        st.write("• Behind-the-scenes - 25% more subscribers")
                                        st.write("• Live streaming - 5x more real-time engagement")
                                    elif platform == "tiktok":
                                        st.info("**Current TikTok Trends:**")
                                        st.write("• Trending sounds - 80% higher reach")
                                        st.write("• Duet features - 3x more engagement")
                                        st.write("• Hashtag challenges - 5x more discoverability")
                                        st.write("• Behind-the-scenes - 2x more followers")
                                        st.write("• User-generated content - 4x more shares")
                                    elif platform == "instagram":
                                        st.info("**Current Instagram Trends:**")
                                        st.write("• Reels over posts - 3x more reach")
                                        st.write("• Carousel posts - 2x more engagement")
                                        st.write("• Interactive stories - 40% more views")
                                        st.write("• IGTV for longer content - higher retention")
                                        st.write("• Collaborations - 2x more followers")
                                    else:  # facebook
                                        st.info("**Current Facebook Trends:**")
                                        st.write("• Video content over text - 4x more engagement")
                                        st.write("• Live streaming - 6x more real-time interaction")
                                        st.write("• Group engagement - 3x more community building")
                                        st.write("• Reels and Stories - 2x more reach")
                                        st.write("• Local business content - higher local engagement")
                        
                        # Generate video with AI content
                        st.info("🎬 Now generating video with AI content...")
                        video_path = generate_ai_video(video_topic, video_style, video_length, script)
                        
                        if video_path and os.path.exists(video_path):
                            st.success("🎉 Your AI-powered video is ready!")
                            
                            # Show video
                            st.video(video_path)
                            
                            # Video info
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Duration", f"{video_length} seconds")
                            with col2:
                                st.metric("Quality", "Full HD")
                            with col3:
                                st.metric("Format", "MP4")
                            
                            # Download button
                            with open(video_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download AI Video",
                                    data=f.read(),
                                    file_name=f"ai_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                                    mime="video/mp4"
                                )
                            
                            # Show file location
                            st.info(f"💾 Video saved to: `{video_path}`")
                            
                            # Add to session state for tracking
                            if 'generated_videos' not in st.session_state:
                                st.session_state.generated_videos = []
                            st.session_state.generated_videos.append({
                                'topic': video_topic,
                                'path': video_path,
                                'timestamp': datetime.now(),
                                'duration': video_length,
                                'ai_generated': True,
                                'script': script
                            })
                        else:
                            st.error("❌ Video generation failed. Please try again.")
                            
                    except Exception as e:
                        st.error(f"❌ AI content generation failed: {str(e)}")
                        st.info("🔄 Falling back to basic video generation...")
                        
                        # Fallback to basic video generation
                        video_path = generate_real_video(video_topic, video_style, video_length)
                        
                        if video_path and os.path.exists(video_path):
                            st.success("🎉 Basic video generated successfully!")
                            st.video(video_path)
                        else:
                            st.error("❌ Video generation failed. Please try again.")
            else:
                st.warning("⚠️ Please enter a video topic")

def generate_real_video(topic, style, duration):
    """Generate a professional, engaging video with real content and effects"""
    if not OPENCV_AVAILABLE:
        st.error("OpenCV is not available. Cannot generate videos.")
        return None
        
    try:
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"professional_video_{timestamp}.mp4"
        video_path = os.path.join(output_dir, filename)
        
        # Video settings for professional quality
        fps = 30
        width, height = 1920, 1080  # Full HD
        total_frames = duration * fps
        
        # Create video writer with H264 codec for better quality
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            st.error("Failed to create video writer. Trying alternative codec...")
            # Fallback to AVI with MJPG
            filename = f"professional_video_{timestamp}.avi"
            video_path = os.path.join(output_dir, filename)
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                st.error("Video writer creation failed. Please check OpenCV installation.")
                return None
        
        st.info(f"🎬 Generating professional {duration}s video: '{topic}' in {style} style...")
        
        # Generate professional video content
        for frame_num in range(total_frames):
            # Create professional frame with multiple elements
            frame = create_professional_frame(topic, style, frame_num, total_frames, width, height)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        
        # Verify the video was created and has content
        if os.path.exists(video_path) and os.path.getsize(video_path) > 1000:
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            st.success(f"✅ Professional video generated successfully!")
            st.info(f"📁 File: {os.path.basename(video_path)}")
            st.info(f"📊 Size: {file_size_mb:.1f} MB")
            st.info(f"🎬 Quality: {width}x{height} @ {fps}fps")
            st.info(f"⏱️ Duration: {duration} seconds")
            return video_path
        else:
            st.error("Video file was created but appears to be empty or too small")
            return None
        
    except Exception as e:
        st.error(f"Error generating professional video: {str(e)}")
        st.info("Trying fallback method...")
        return generate_simple_video(topic, style, duration)

def create_professional_frame(topic, style, frame_num, total_frames, width, height):
    """Create a professional video frame with multiple elements and effects"""
    # Create background with gradient
    frame = create_gradient_background(style, width, height)
    
    # Calculate timing for different sections
    progress = frame_num / total_frames
    section_duration = 1.0 / 4  # 4 sections: intro, content, highlight, outro
    
    # Add topic-specific visual elements (this is the key improvement!)
    frame = create_topic_visuals(frame, topic, style, progress, width, height)
    
    # Section 1: Intro (0-25%)
    if progress < 0.25:
        frame = add_intro_section(frame, topic, style, progress * 4, width, height)
    
    # Section 2: Main Content (25-50%)
    elif progress < 0.5:
        frame = add_content_section(frame, topic, style, (progress - 0.25) * 4, width, height)
    
    # Section 3: Highlight (50-75%)
    elif progress < 0.75:
        frame = add_highlight_section(frame, topic, style, (progress - 0.5) * 4, width, height)
    
    # Section 4: Outro (75-100%)
    else:
        frame = add_outro_section(frame, topic, style, (progress - 0.75) * 4, width, height)
    
    # Add dynamic elements
    frame = add_dynamic_elements(frame, frame_num, total_frames, width, height)
    
    # Add professional overlays
    frame = add_professional_overlays(frame, style, frame_num, total_frames, width, height)
    
    return frame

def create_gradient_background(style, width, height):
    """Create a professional gradient background based on style"""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    if style == "Professional":
        # Blue to dark blue gradient
        for y in range(height):
            ratio = y / height
            color = (
                int(50 + ratio * 100),
                int(100 + ratio * 50),
                int(150 + ratio * 100)
            )
            frame[y, :] = color
    
    elif style == "Creative":
        # Purple to pink gradient
        for y in range(height):
            ratio = y / height
            color = (
                int(100 + ratio * 100),
                int(50 + ratio * 50),
                int(150 + ratio * 100)
            )
            frame[y, :] = color
    
    elif style == "Educational":
        # Green to blue gradient
        for y in range(height):
            ratio = y / height
            color = (
                int(50 + ratio * 50),
                int(150 + ratio * 50),
                int(100 + ratio * 100)
            )
            frame[y, :] = color
    
    elif style == "Entertainment":
        # Orange to red gradient
        for y in range(height):
            ratio = y / height
            color = (
                int(200 + ratio * 55),
                int(100 + ratio * 50),
                int(50 + ratio * 100)
            )
            frame[y, :] = color
    
    else:  # Corporate
        # Gray to dark gray gradient
        for y in range(height):
            ratio = y / height
            color = (
                int(100 + ratio * 50),
                int(100 + ratio * 50),
                int(100 + ratio * 50)
            )
            frame[y, :] = color
    
    return frame

def add_intro_section(frame, topic, style, progress, width, height):
    """Add intro section with animated title and style indicator"""
    # Animated title entrance
    title_alpha = min(1.0, progress * 3)  # Fade in over 1/3 of section
    
    # Main title with shadow effect
    title_text = topic[:40] + "..." if len(topic) > 40 else topic
    title_size = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_DUPLEX, 2.5, 4)[0]
    title_x = (width - title_size[0]) // 2
    title_y = height // 2
    
    # Shadow
    cv2.putText(frame, title_text, (title_x + 3, title_y + 3), 
                cv2.FONT_HERSHEY_DUPLEX, 2.5, (0, 0, 0), 4)
    
    # Main text
    cv2.putText(frame, title_text, (title_x, title_y), 
                cv2.FONT_HERSHEY_DUPLEX, 2.5, (255, 255, 255), 4)
    
    # Style indicator with animation
    style_alpha = min(1.0, max(0, (progress - 0.5) * 2))
    if style_alpha > 0:
        style_text = f"Style: {style}"
        style_size = cv2.getTextSize(style_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        style_x = (width - style_size[0]) // 2
        style_y = title_y + 100
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (style_x - 20, style_y - 30), 
                     (style_x + style_size[0] + 20, style_y + 10), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 1 - style_alpha, frame, style_alpha, 0)
        
        cv2.putText(frame, style_text, (style_x, style_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    return frame

def add_content_section(frame, topic, style, progress, width, height):
    """Add main content section with key points and animations"""
    # Content points based on topic and style
    content_points = generate_content_points(topic, style)
    
    # Animate content points
    for i, point in enumerate(content_points[:3]):  # Show max 3 points
        point_progress = max(0, min(1, (progress - i * 0.3) * 2))
        if point_progress > 0:
            # Point background
            point_y = 200 + i * 120
            point_width = int(800 * point_progress)
            point_x = (width - point_width) // 2
            
            # Animated background
            cv2.rectangle(frame, (point_x, point_y - 20), 
                         (point_x + point_width, point_y + 40), (255, 255, 255), -1)
            cv2.rectangle(frame, (point_x, point_y - 20), 
                         (point_x + point_width, point_y + 40), (100, 100, 100), 2)
            
            # Point text
            cv2.putText(frame, f"• {point}", (point_x + 20, point_y + 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    return frame

def add_highlight_section(frame, topic, style, progress, width, height):
    """Add highlight section with visual effects and emphasis"""
    # Central highlight with glow effect
    highlight_alpha = min(1.0, progress * 2)
    
    if highlight_alpha > 0:
        # Glow effect
        for radius in range(20, 0, -2):
            alpha = highlight_alpha * (radius / 20)
            cv2.circle(frame, (width // 2, height // 2), radius, (255, 255, 0), -1)
        
        # Main highlight circle
        cv2.circle(frame, (width // 2, height // 2), 30, (255, 255, 255), -1)
        cv2.circle(frame, (width // 2, height // 2), 30, (0, 0, 0), 3)
        
        # Highlight text
        highlight_text = "KEY POINT"
        text_size = cv2.getTextSize(highlight_text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = height // 2 + 80
        
        cv2.putText(frame, highlight_text, (text_x, text_y), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)
    
    return frame

def add_outro_section(frame, topic, style, progress, width, height):
    """Add outro section with call to action and branding"""
    # Fade in outro elements
    outro_alpha = min(1.0, progress * 3)
    
    if outro_alpha > 0:
        # Call to action
        cta_text = "Ready to Create Your Own?"
        cta_size = cv2.getTextSize(cta_text, cv2.FONT_HERSHEY_DUPLEX, 1.8, 3)[0]
        cta_x = (width - cta_size[0]) // 2
        cta_y = height // 2 - 50
        
        cv2.putText(frame, cta_text, (cta_x, cta_y), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 3)
        
        # Branding
        brand_text = "MoneyPrinterTurboPro"
        brand_size = cv2.getTextSize(brand_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        brand_x = (width - brand_size[0]) // 2
        brand_y = height // 2 + 50
        
        cv2.putText(frame, brand_text, (brand_x, brand_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 200), 2)
    
    return frame

def add_dynamic_elements(frame, frame_num, total_frames, width, height):
    """Add dynamic elements like particles, moving objects, etc."""
    # Animated particles
    for i in range(5):
        particle_x = int((frame_num + i * 100) % width)
        particle_y = int((frame_num + i * 150) % height)
        particle_size = 2 + (frame_num % 3)
        
        cv2.circle(frame, (particle_x, particle_y), particle_size, (255, 255, 255), -1)
    
    # Moving accent lines
    line_y = int((frame_num * 2) % height)
    cv2.line(frame, (0, line_y), (width, line_y), (255, 255, 255, 100), 2)
    
    return frame

def add_professional_overlays(frame, style, frame_num, total_frames, width, height):
    """Add professional overlays like progress bar, branding, etc."""
    # Progress bar at bottom
    progress = frame_num / total_frames
    bar_width = int(width * 0.8)
    bar_height = 8
    bar_x = (width - bar_width) // 2
    bar_y = height - 50
    
    # Background bar
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                  (100, 100, 100), -1)
    
    # Progress bar
    progress_width = int(bar_width * progress)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), 
                  (0, 255, 0), -1)
    
    # Corner branding
    brand_text = "MPTP"
    cv2.putText(frame, brand_text, (width - 100, height - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    return frame

def generate_content_points(topic, style):
    """Generate relevant content points based on topic and style"""
    if style == "Professional":
        return [
            "Clear and structured approach",
            "Data-driven insights",
            "Professional presentation",
            "Actionable recommendations"
        ]
    elif style == "Creative":
        return [
            "Innovative thinking",
            "Unique perspectives",
            "Creative solutions",
            "Out-of-the-box ideas"
        ]
    elif style == "Educational":
        return [
            "Step-by-step learning",
            "Practical examples",
            "Key concepts explained",
            "Hands-on practice"
        ]
    elif style == "Entertainment":
        return [
            "Engaging content",
            "Fun and interactive",
            "Memorable experiences",
            "Entertainment value"
        ]
    else:  # Corporate
        return [
            "Strategic planning",
            "Business objectives",
            "Performance metrics",
            "Growth opportunities"
        ]

def create_topic_visuals(frame, topic, style, progress, width, height):
    """Create visual elements that represent the topic"""
    # Convert topic to lowercase for easier matching
    topic_lower = topic.lower()
    
    # Create visual elements based on topic keywords
    if any(word in topic_lower for word in ['garden', 'plant', 'flower', 'tree']):
        frame = add_gardening_visuals(frame, progress, width, height)
    elif any(word in topic_lower for word in ['cook', 'food', 'recipe', 'kitchen']):
        frame = add_cooking_visuals(frame, progress, width, height)
    elif any(word in topic_lower for word in ['tech', 'computer', 'software', 'app']):
        frame = add_tech_visuals(frame, progress, width, height)
    elif any(word in topic_lower for word in ['business', 'marketing', 'sales', 'strategy']):
        frame = add_business_visuals(frame, progress, width, height)
    elif any(word in topic_lower for word in ['health', 'fitness', 'exercise', 'wellness']):
        frame = add_health_visuals(frame, progress, width, height)
    else:
        frame = add_generic_visuals(frame, topic, progress, width, height)
    
    return frame

def add_gardening_visuals(frame, progress, width, height):
    """Add advanced gardening-related visual elements with sophisticated graphics"""
    # Animated growing plants with advanced graphics
    plant_alpha = min(1.0, progress * 2)
    if plant_alpha > 0:
        # Enhanced plant pot with 3D effect
        pot_x, pot_y = width // 2, height - 200
        
        # 3D pot effect with multiple layers
        for layer in range(5):
            layer_alpha = 1.0 - (layer * 0.15)
            layer_width = 40 - layer * 2
            layer_y = pot_y + layer * 8
            color = (int(139 * layer_alpha), int(69 * layer_alpha), int(19 * layer_alpha))
            cv2.rectangle(frame, (pot_x - layer_width, layer_y), (pot_x + layer_width, layer_y + 12), color, -1)
        
        # Growing plant with realistic stem
        plant_height = int(50 + progress * 120)
        plant_color = (34, 139, 34)  # Forest green
        
        # Curved stem with multiple segments
        stem_points = []
        for i in range(10):
            segment_progress = i / 9.0
            segment_height = int(segment_progress * plant_height)
            # Add slight curve to stem
            curve_offset = int(10 * np.sin(segment_progress * np.pi))
            stem_points.append((pot_x + curve_offset, pot_y - segment_height))
        
        # Draw curved stem
        for i in range(len(stem_points) - 1):
            cv2.line(frame, stem_points[i], stem_points[i + 1], plant_color, 6)
        
        # Advanced leaf system with realistic shapes
        leaf_count = int(5 + progress * 8)
        for i in range(leaf_count):
            leaf_angle = (i * 360 / leaf_count + progress * 180) % 360
            leaf_distance = int(30 + progress * 40)
            leaf_x = pot_x + int(leaf_distance * np.cos(np.radians(leaf_angle)))
            leaf_y = pot_y - int(plant_height * 0.7) + int(leaf_distance * np.sin(np.radians(leaf_angle)))
            
            # Create realistic leaf shape
            leaf_size = int(15 + progress * 20)
            leaf_color = (int(34 + progress * 50), 139, int(34 + progress * 30))
            
            # Leaf with veins
            cv2.ellipse(frame, (leaf_x, leaf_y), (leaf_size, leaf_size//2), leaf_angle, 0, 360, leaf_color, -1)
            # Vein lines
            cv2.line(frame, (leaf_x, leaf_y), (leaf_x + int(leaf_size * 0.8), leaf_y), (20, 100, 20), 2)
        
        # Advanced flower system
        if progress > 0.4:
            flower_count = int(3 + progress * 7)
            for i in range(flower_count):
                flower_angle = (i * 360 / flower_count + progress * 360) % 360
                flower_distance = int(25 + progress * 35)
                flower_x = pot_x + int(flower_distance * np.cos(np.radians(flower_angle)))
                flower_y = pot_y - int(plant_height * 0.9) + int(flower_distance * np.sin(np.radians(flower_angle)))
                
                # Multi-petal flowers
                petal_count = 8
                for petal in range(petal_count):
                    petal_angle = flower_angle + (petal * 360 / petal_count)
                    petal_x = flower_x + int(12 * np.cos(np.radians(petal_angle)))
                    petal_y = flower_y + int(12 * np.sin(np.radians(petal_angle)))
                    
                    # Flower colors based on progress
                    if progress < 0.6:
                        flower_color = (255, 255, 0)  # Yellow buds
                    elif progress < 0.8:
                        flower_color = (255, 165, 0)  # Orange blooming
                    else:
                        flower_color = (255, 20, 147)  # Pink full bloom
                    
                    cv2.circle(frame, (petal_x, petal_y), 6, flower_color, -1)
                
                # Flower center
                cv2.circle(frame, (flower_x, flower_y), 8, (139, 69, 19), -1)
        
        # Animated soil and roots
        if progress > 0.2:
            # Soil particles
            for i in range(20):
                soil_x = pot_x - 50 + (i * 10) % 100
                soil_y = pot_y + 60 + (i % 3) * 5
                soil_size = 2 + (i % 3)
                soil_color = (101, 67, 33)
                cv2.circle(frame, (soil_x, soil_y), soil_size, soil_color, -1)
            
            # Root system
            root_count = int(3 + progress * 5)
            for i in range(root_count):
                root_angle = (i * 120 + progress * 90) % 360
                root_length = int(20 + progress * 30)
                root_x = pot_x + int(root_length * np.cos(np.radians(root_angle)))
                root_y = pot_y + 60 + int(root_length * np.sin(np.radians(root_angle)))
                cv2.line(frame, (pot_x, pot_y + 60), (root_x, root_y), (139, 69, 19), 3)
        
        # Animated water droplets
        if progress > 0.3:
            for i in range(5):
                droplet_x = pot_x - 60 + (i * 25) % 120
                droplet_y = pot_y - 100 + int((progress * 50 + i * 10) % 60)
                droplet_size = 3 + (i % 3)
                # Water effect with transparency simulation
                cv2.circle(frame, (droplet_x, droplet_y), droplet_size, (173, 216, 230), -1)
                cv2.circle(frame, (droplet_x, droplet_y), droplet_size, (135, 206, 235), 1)
    
    return frame

def add_cooking_visuals(frame, progress, width, height):
    """Add advanced cooking-related visual elements with sophisticated graphics"""
    # Animated cooking elements with advanced graphics
    if progress > 0:
        # Enhanced 3D pan with realistic details
        pan_x, pan_y = width // 2, height - 150
        
        # Pan body with 3D effect
        for layer in range(8):
            layer_alpha = 1.0 - (layer * 0.1)
            layer_width = 80 - layer * 3
            layer_y = pan_y + layer * 3
            color = (int(64 * layer_alpha), int(64 * layer_alpha), int(64 * layer_alpha))
            cv2.ellipse(frame, (pan_x, layer_y), (layer_width, 20 - layer * 2), 0, 0, 180, color, -1)
        
        # Pan handle with realistic design
        handle_start_x = pan_x + 80
        handle_start_y = pan_y - 10
        handle_end_x = handle_start_x + 60
        handle_end_y = handle_start_y - 20
        
        # Handle with 3D effect
        for i in range(5):
            handle_width = 8 - i * 1
            handle_y = handle_start_y - i * 2
            handle_color = (int(139 * (1.0 - i * 0.15)), int(69 * (1.0 - i * 0.15)), int(19 * (1.0 - i * 0.15)))
            cv2.line(frame, (handle_start_x, handle_y), (handle_end_x, handle_y), handle_color, handle_width)
        
        # Advanced steam animation with realistic physics
        steam_count = int(5 + progress * 8)
        for i in range(steam_count):
            steam_x = pan_x - 60 + (i * 25) % 120
            steam_y = pan_y - int(25 + progress * 40 + (i * 5) % 20)
            steam_size = int(4 + progress * 12 + (i % 3) * 2)
            
            # Steam with transparency effect
            steam_color = (int(200 + progress * 55), int(200 + progress * 55), int(200 + progress * 55))
            cv2.circle(frame, (steam_x, steam_y), steam_size, steam_color, -1)
            cv2.circle(frame, (steam_x, steam_y), steam_size, (255, 255, 255), 1)
            
            # Steam trail effect
            for trail in range(3):
                trail_y = steam_y + trail * 8
                trail_size = steam_size - trail * 2
                if trail_size > 0:
                    trail_alpha = 1.0 - (trail * 0.3)
                    trail_color = (int(steam_color[0] * trail_alpha), int(steam_color[1] * trail_alpha), int(steam_color[2] * trail_alpha))
                    cv2.circle(frame, (steam_x, trail_y), trail_size, trail_color, -1)
        
        # Advanced ingredient system
        if progress > 0.2:
            # Vegetable cutting board
            board_x, board_y = pan_x - 150, pan_y - 80
            board_width, board_height = 120, 80
            
            # Wooden cutting board with grain effect
            cv2.rectangle(frame, (board_x, board_y), (board_x + board_width, board_y + board_height), (139, 69, 19), -1)
            cv2.rectangle(frame, (board_x, board_y), (board_x + board_width, board_y + board_height), (101, 67, 33), 3)
            
            # Wood grain lines
            for i in range(8):
                grain_y = board_y + 10 + i * 10
                grain_length = int(80 + (i % 3) * 20)
                grain_x = board_x + 20 + (i % 2) * 20
                cv2.line(frame, (grain_x, grain_y), (grain_x + grain_length, grain_y), (101, 67, 33), 1)
            
            # Animated vegetables with realistic shapes
            veg_positions = [
                (board_x + 20, board_y + 20, "carrot"),
                (board_x + 60, board_y + 30, "tomato"),
                (board_x + 40, board_y + 50, "onion"),
                (board_x + 80, board_y + 50, "bell_pepper")
            ]
            
            for i, (veg_x, veg_y, veg_type) in enumerate(veg_positions):
                veg_progress = max(0, min(1, (progress - 0.2 - i * 0.1) * 3))
                if veg_progress > 0:
                    if veg_type == "carrot":
                        # Carrot shape
                        cv2.ellipse(frame, (veg_x, veg_y), (8, 15), 0, 0, 360, (255, 165, 0), -1)
                        cv2.ellipse(frame, (veg_x, veg_y), (8, 15), 0, 0, 360, (255, 140, 0), 2)
                        # Carrot top
                        cv2.ellipse(frame, (veg_x, veg_y - 15), (6, 8), 0, 0, 360, (34, 139, 34), -1)
                    
                    elif veg_type == "tomato":
                        # Tomato with shine effect
                        cv2.circle(frame, (veg_x, veg_y), 12, (255, 0, 0), -1)
                        cv2.circle(frame, (veg_x, veg_y), 12, (139, 0, 0), 2)
                        # Shine highlight
                        cv2.circle(frame, (veg_x - 3, veg_y - 3), 4, (255, 255, 255), -1)
                    
                    elif veg_type == "onion":
                        # Onion layers
                        for layer in range(3):
                            layer_size = 10 - layer * 2
                            layer_color = (255, 255, 255) if layer == 0 else (255, 220, 220)
                            cv2.circle(frame, (veg_x, veg_y), layer_size, layer_color, -1)
                            cv2.circle(frame, (veg_x, veg_y), layer_size, (200, 200, 200), 1)
                    
                    elif veg_type == "bell_pepper":
                        # Bell pepper with realistic shape
                        cv2.ellipse(frame, (veg_x, veg_y), (10, 12), 0, 0, 360, (0, 255, 0), -1)
                        cv2.ellipse(frame, (veg_x, veg_y), (10, 12), 0, 0, 360, (0, 200, 0), 2)
                        # Pepper top
                        cv2.ellipse(frame, (veg_x, veg_y - 12), (8, 6), 0, 0, 360, (34, 139, 34), -1)
        
        # Animated cooking effects
        if progress > 0.5:
            # Bubbling effect in pan
            bubble_count = int(3 + progress * 5)
            for i in range(bubble_count):
                bubble_x = pan_x - 40 + (i * 20) % 80
                bubble_y = pan_y - 5 + int((progress * 20 + i * 10) % 15)
                bubble_size = 3 + (i % 3)
                
                # Bubble with shine
                cv2.circle(frame, (bubble_x, bubble_y), bubble_size, (255, 255, 255), -1)
                cv2.circle(frame, (bubble_x, bubble_y), bubble_size, (200, 200, 200), 1)
                # Bubble highlight
                cv2.circle(frame, (bubble_x - 1, bubble_y - 1), 1, (255, 255, 255), -1)
            
            # Heat waves effect
            wave_count = int(2 + progress * 3)
            for i in range(wave_count):
                wave_y = pan_y - 30 - i * 15
                wave_amplitude = int(5 + progress * 10)
                wave_frequency = 0.02
                
                for x in range(pan_x - 60, pan_x + 60, 5):
                    wave_x = x
                    wave_offset = int(wave_amplitude * np.sin(x * wave_frequency + progress * 10))
                    cv2.circle(frame, (wave_x, wave_y + wave_offset), 1, (255, 255, 200), -1)
    
    return frame

def add_tech_visuals(frame, progress, width, height):
    """Add advanced technology-related visual elements with sophisticated graphics"""
    # Advanced circuit board pattern with realistic tech elements
    if progress > 0:
        # Enhanced circuit grid with multiple layers
        for layer in range(3):
            layer_alpha = 1.0 - (layer * 0.2)
            layer_spacing = 80 + layer * 20
            layer_color = (int(0 * layer_alpha), int(255 * layer_alpha), int(255 * layer_alpha))
            
            for i in range(0, width, layer_spacing):
                for j in range(0, height, layer_spacing):
                    if (i + j + layer * 50) % (layer_spacing * 2) == 0:
                        # Circuit node with 3D effect
                        for depth in range(3):
                            node_size = 8 - depth * 2
                            node_color = (int(layer_color[0] * (1.0 - depth * 0.3)), 
                                        int(layer_color[1] * (1.0 - depth * 0.3)), 
                                        int(layer_color[2] * (1.0 - depth * 0.3)))
                            cv2.circle(frame, (i, j), node_size, node_color, -1)
                        
                        # Enhanced connecting lines with glow effect
                        if i + layer_spacing < width:
                            # Horizontal connection
                            for glow in range(3):
                                glow_width = 3 - glow
                                if glow_width > 0:
                                    glow_color = (int(layer_color[0] * (1.0 - glow * 0.3)), 
                                                int(layer_color[1] * (1.0 - glow * 0.3)), 
                                                int(layer_color[2] * (1.0 - glow * 0.3)))
                                    cv2.line(frame, (i, j), (i + layer_spacing, j), glow_color, glow_width)
                        
                        if j + layer_spacing < height:
                            # Vertical connection
                            for glow in range(3):
                                glow_width = 3 - glow
                                if glow_width > 0:
                                    glow_color = (int(layer_color[0] * (1.0 - glow * 0.3)), 
                                                int(layer_color[1] * (1.0 - glow * 0.3)), 
                                                int(layer_color[2] * (1.0 - glow * 0.3)))
                                    cv2.line(frame, (i, j), (i, j + layer_spacing), glow_color, glow_width)
        
        # Advanced data flow with particle system
        data_alpha = min(1.0, progress * 3)
        if data_alpha > 0:
            data_particle_count = int(8 + progress * 12)
            for i in range(data_particle_count):
                # Complex particle movement patterns
                base_x = int((progress * 1200 + i * 150) % width)
                base_y = int((progress * 800 + i * 120) % height)
                
                # Add wave motion to particles
                wave_offset = int(20 * np.sin(progress * 8 + i * 0.5))
                data_x = base_x + wave_offset
                data_y = base_y + int(15 * np.cos(progress * 6 + i * 0.3))
                
                # Particle with trail effect
                particle_size = 4 + (i % 3) * 2
                particle_color = (255, 255, 0) if i % 2 == 0 else (0, 255, 255)
                
                # Main particle
                cv2.circle(frame, (data_x, data_y), particle_size, particle_color, -1)
                
                # Particle trail
                for trail in range(3):
                    trail_x = data_x - int(trail * 8 * np.cos(progress * 4))
                    trail_y = data_y - int(trail * 8 * np.sin(progress * 4))
                    trail_size = particle_size - trail
                    if trail_size > 0:
                        trail_alpha = 1.0 - (trail * 0.3)
                        trail_color = (int(particle_color[0] * trail_alpha), 
                                     int(particle_color[1] * trail_alpha), 
                                     int(particle_color[2] * trail_alpha))
                        cv2.circle(frame, (trail_x, trail_y), trail_size, trail_color, -1)
        
        # Holographic display effect
        if progress > 0.3:
            holo_center_x, holo_center_y = width // 2, height // 2
            holo_radius = int(80 + progress * 120)
            
            # Holographic rings
            for ring in range(3):
                ring_radius = holo_radius - ring * 20
                ring_alpha = 1.0 - (ring * 0.3)
                ring_color = (int(0 * ring_alpha), int(255 * ring_alpha), int(255 * ring_alpha))
                
                # Animated ring with rotation
                ring_rotation = progress * 360 + ring * 120
                for angle in range(0, 360, 10):
                    rad_angle = np.radians(angle + ring_rotation)
                    x1 = holo_center_x + int(ring_radius * np.cos(rad_angle))
                    y1 = holo_center_y + int(ring_radius * np.sin(rad_angle))
                    x2 = holo_center_x + int(ring_radius * np.cos(rad_angle + np.radians(10)))
                    y2 = holo_center_y + int(ring_radius * np.sin(rad_angle + np.radians(10)))
                    
                    # Glowing effect
                    for glow in range(2):
                        glow_width = 2 - glow
                        if glow_width > 0:
                            glow_color = (int(ring_color[0] * (1.0 - glow * 0.5)), 
                                        int(ring_color[1] * (1.0 - glow * 0.5)), 
                                        int(ring_color[2] * (1.0 - glow * 0.5)))
                            cv2.line(frame, (x1, y1), (x2, y2), glow_color, glow_width)
        
        # Digital rain effect (Matrix-style)
        if progress > 0.6:
            rain_count = int(5 + progress * 8)
            for i in range(rain_count):
                rain_x = int((i * 200 + progress * 300) % width)
                rain_y = int((progress * 600 + i * 100) % height)
                rain_length = int(20 + progress * 30)
                
                # Rain drop with glow
                for glow in range(2):
                    glow_color = (0, int(255 * (1.0 - glow * 0.5)), 0)
                    cv2.line(frame, (rain_x, rain_y), (rain_x, rain_y + rain_length), glow_color, 2 - glow)
                
                # Rain drop characters (simplified)
                char_y = rain_y + rain_length // 2
                cv2.putText(frame, "1", (rain_x - 3, char_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Floating UI elements
        if progress > 0.4:
            ui_elements = [
                (width // 4, height // 4, "CPU", (255, 0, 255)),
                (3 * width // 4, height // 4, "RAM", (0, 255, 255)),
                (width // 4, 3 * height // 4, "GPU", (255, 255, 0)),
                (3 * width // 4, 3 * height // 4, "NET", (0, 255, 0))
            ]
            
            for i, (ui_x, ui_y, ui_label, ui_color) in enumerate(ui_elements):
                ui_progress = max(0, min(1, (progress - 0.4 - i * 0.1) * 3))
                if ui_progress > 0:
                    # UI box with 3D effect
                    box_size = int(30 + ui_progress * 20)
                    for depth in range(3):
                        depth_alpha = 1.0 - (depth * 0.2)
                        depth_color = (int(ui_color[0] * depth_alpha), 
                                     int(ui_color[1] * depth_alpha), 
                                     int(ui_color[2] * depth_alpha))
                        cv2.rectangle(frame, (ui_x - box_size + depth * 2, ui_y - box_size + depth * 2),
                                     (ui_x + box_size - depth * 2, ui_y + box_size - depth * 2), depth_color, -1)
                    
                    # UI label
                    cv2.putText(frame, ui_label, (ui_x - 15, ui_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Animated progress bar
                    progress_bar_width = int(box_size * 1.5)
                    progress_bar_height = 4
                    progress_bar_x = ui_x - progress_bar_width // 2
                    progress_bar_y = ui_y + box_size + 10
                    
                    # Background bar
                    cv2.rectangle(frame, (progress_bar_x, progress_bar_y), 
                                 (progress_bar_x + progress_bar_width, progress_bar_y + progress_bar_height), 
                                 (100, 100, 100), -1)
                    
                    # Animated fill
                    fill_width = int(progress_bar_width * ui_progress)
                    cv2.rectangle(frame, (progress_bar_x, progress_bar_y), 
                                 (progress_bar_x + fill_width, progress_bar_y + progress_bar_height), 
                                 ui_color, -1)
    
    return frame

def add_business_visuals(frame, progress, width, height):
    """Add business-related visual elements"""
    # Charts and graphs
    if progress > 0:
        # Bar chart
        chart_x, chart_y = width // 2, height - 150
        bar_width = 40
        bar_spacing = 60
        
        for i in range(4):
            bar_height = int(30 + progress * 70 + (i * 10))
            bar_x = chart_x - 90 + i * bar_spacing
            bar_y = chart_y - bar_height
            
            # Bar
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, chart_y), (100, 150, 255), -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, chart_y), (50, 75, 127), 2)
        
        # Trend line
        if progress > 0.5:
            line_alpha = min(1.0, (progress - 0.5) * 2)
            points = []
            for i in range(5):
                x = chart_x - 90 + i * bar_spacing + bar_width // 2
                y = chart_y - int(30 + progress * 70 + (i * 10))
                points.append((x, y))
            
            for i in range(len(points) - 1):
                cv2.line(frame, (points[i][0], points[i][1]), (points[i + 1][0], points[i + 1][1]), (255, 255, 0), 3)
    
    return frame

def add_health_visuals(frame, progress, width, height):
    """Add health and fitness visual elements"""
    # Animated fitness elements
    if progress > 0:
        # Heart beat animation
        heart_x, heart_y = width // 2, height - 200
        heart_size = int(20 + progress * 15)
        
        # Heart shape (simplified)
        cv2.circle(frame, (heart_x - heart_size//2, heart_y), heart_size//2, (255, 0, 0), -1)
        cv2.circle(frame, (heart_x + heart_size//2, heart_y), (heart_size//2), (255, 0, 0), -1)
        
        # Connecting curves (simplified)
        cv2.line(frame, (heart_x - heart_size//2, heart_y), (heart_x, heart_y + heart_size), (255, 0, 0), 3)
        cv2.line(frame, (heart_x + heart_size//2, heart_y), (heart_x, heart_y + heart_size), (255, 0, 0), 3)
        
        # Pulse effect
        pulse_alpha = abs(np.sin(progress * 10)) * 0.5 + 0.5
        cv2.circle(frame, (heart_x, heart_y), int(heart_size * 1.5), (255, 0, 0), int(3 * pulse_alpha))
    
    return frame

def add_generic_visuals(frame, topic, progress, width, height):
    """Add generic visual elements for any topic"""
    # Abstract geometric patterns
    if progress > 0:
        # Rotating geometric shapes
        center_x, center_y = width // 2, height // 2
        rotation = progress * 360
        
        # Triangle
        triangle_points = []
        for i in range(3):
            angle = rotation + i * 120
            x = center_x + int(50 * np.cos(np.radians(angle)))
            y = center_y + int(50 * np.sin(np.radians(angle)))
            triangle_points.append((x, y))
        
        cv2.polylines(frame, [np.array(triangle_points)], True, (255, 255, 255), 3)
        
        # Expanding circles
        circle_radius = int(30 + progress * 100)
        cv2.circle(frame, (center_x, center_y), circle_radius, (100, 150, 255), 2)
        
        # Floating particles
        for i in range(8):
            particle_x = int(center_x + (progress * 200 - 100) * np.cos(np.radians(i * 45 + rotation)))
            particle_y = int(center_y + (progress * 200 - 100) * np.sin(np.radians(i * 45 + rotation)))
            cv2.circle(frame, (particle_x, particle_y), 4, (255, 255, 0), -1)
    
    return frame

def generate_simple_video(topic, style, duration):
    """Fallback method to generate a simple video using PIL and basic animation"""
    if not PIL_AVAILABLE:
        st.error("PIL not available for fallback video generation")
        return None
        
    try:
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_video_{timestamp}.gif"
        video_path = os.path.join(output_dir, filename)
        
        # Create a simple animated GIF instead
        frames = []
        fps = 10
        total_frames = duration * fps
        
        for frame_num in range(total_frames):
            # Create a simple frame
            img = Image.new('RGB', (800, 600), color=get_style_color(style))
            draw = ImageDraw.Draw(img)
            
            # Add topic text
            text = topic[:40] + "..." if len(topic) > 40 else topic
            draw.text((400, 300), text, fill=(255, 255, 255))
            
            # Add frame counter
            draw.text((50, 50), f"Frame {frame_num + 1}/{total_frames}", fill=(255, 255, 255))
            
            # Add progress indicator
            progress = (frame_num + 1) / total_frames
            bar_width = int(600 * progress)
            draw.rectangle([100, 500, 100 + bar_width, 520], fill=(0, 255, 0))
            
            frames.append(img)
        
        # Save as animated GIF
        frames[0].save(
            video_path,
            save_all=True,
            append_images=frames[1:],
            duration=1000//fps,  # Duration in milliseconds
            loop=0
        )
        
        st.success(f"✅ Simple video (GIF) generated: {os.path.basename(video_path)}")
        return video_path
        
    except Exception as e:
        st.error(f"Fallback video generation also failed: {str(e)}")
        return None

def get_style_color(style):
    """Get background color for different styles"""
    if style == "Professional":
        return (50, 50, 100)  # Dark blue
    elif style == "Creative":
        return (100, 50, 100)  # Purple
    elif style == "Educational":
        return (50, 100, 50)  # Green
    elif style == "Entertainment":
        return (100, 100, 50)  # Yellow-green
    elif style == "Corporate":
        return (80, 80, 80)  # Gray
    else:
        return (100, 50, 50)  # Red-brown

def generate_ai_video(topic, style, duration, script):
    """Generate a video using AI-generated content and script"""
    if not OPENCV_AVAILABLE:
        st.error("OpenCV is not available. Cannot generate videos.")
        return None
        
    try:
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_video_{timestamp}.mp4"
        video_path = os.path.join(output_dir, filename)
        
        # Video settings for professional quality
        fps = 30
        width, height = 1920, 1080  # Full HD
        total_frames = duration * fps
        
        # Create video writer with H264 codec for better quality
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            st.error("Failed to create video writer. Trying alternative codec...")
            # Fallback to AVI with MJPG
            filename = f"ai_video_{timestamp}.avi"
            video_path = os.path.join(output_dir, filename)
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                st.error("Video writer creation failed. Please check OpenCV installation.")
                return None
        
        st.info(f"🎬 Generating AI-powered {duration}s video: '{topic}' in {style} style...")
        
        # Generate AI-powered video content based on script
        for frame_num in range(total_frames):
            # Create AI-enhanced frame with script content
            frame = create_ai_enhanced_frame(topic, style, frame_num, total_frames, width, height, script)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        
        # Verify the video was created and has content
        if os.path.exists(video_path) and os.path.getsize(video_path) > 1000:
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            st.success(f"✅ AI-powered video generated successfully!")
            st.info(f"📁 File: {os.path.basename(video_path)}")
            st.info(f"📊 Size: {file_size_mb:.1f} MB")
            st.info(f"🎬 Quality: {width}x{height} @ {fps}fps")
            st.info(f"⏱️ Duration: {duration} seconds")
            st.info(f"🤖 AI Content: {script.get('title', 'Custom Script')}")
            return video_path
        else:
            st.error("Video file was created but appears to be empty or too small")
            return None
        
    except Exception as e:
        st.error(f"Error generating AI video: {str(e)}")
        st.info("Trying fallback method...")
        return generate_real_video(topic, style, duration)

def create_ai_enhanced_frame(topic, style, frame_num, total_frames, width, height, script):
    """Create a frame enhanced with AI-generated content"""
    # Create background with gradient
    frame = create_gradient_background(style, width, height)
    
    # Calculate timing for different sections based on script
    progress = frame_num / total_frames
    sections = script.get('sections', [])
    
    # Determine current section based on progress
    current_section = 0
    if sections:
        section_progress = 0
        for i, section in enumerate(sections):
            section_duration = section.get('duration', 5)
            section_progress += section_duration / duration
            if progress <= section_progress:
                current_section = i
                break
    
    # Add AI-generated content to frame
    if sections and current_section < len(sections):
        section = sections[current_section]
        section_title = section.get('title', 'Section')
        section_content = section.get('content', 'Content')
        
        # Add section title
        title_y = height // 3
        cv2.putText(frame, section_title, (width//2 - 300, title_y), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
        
        # Add section content (wrapped text)
        content_y = title_y + 100
        wrapped_content = wrap_text(section_content, width - 200, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        
        for i, line in enumerate(wrapped_content[:3]):  # Show max 3 lines
            y_pos = content_y + i * 50
            cv2.putText(frame, line, (width//2 - 300, y_pos), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    
    # Add AI branding
    ai_text = "🤖 AI-Powered Content"
    cv2.putText(frame, ai_text, (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    # Add video title from script
    video_title = script.get('title', topic)
    title_size = cv2.getTextSize(video_title, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
    title_x = (width - title_size[0]) // 2
    cv2.putText(frame, video_title, (title_x, height - 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    # Add dynamic elements
    frame = add_dynamic_elements(frame, frame_num, total_frames, width, height)
    
    # Add professional overlays
    frame = add_professional_overlays(frame, style, frame_num, total_frames, width, height)
    
    return frame

def wrap_text(text, max_width, font, font_scale, thickness):
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_size = cv2.getTextSize(test_line, font, font_scale, thickness)[0]
        
        if text_size[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def render_advanced_settings():
    st.subheader("Advanced Video Settings")
    st.info("Advanced settings coming soon! For now, use Quick Generate to create real videos.")

def render_batch_processing():
    st.subheader("Batch Video Processing")
    st.info("Batch processing coming soon! For now, use Quick Generate to create real videos.")

def show_video_history():
    st.subheader("📚 Recently Generated Videos")
    
    if 'generated_videos' in st.session_state and st.session_state.generated_videos:
        for i, video in enumerate(st.session_state.generated_videos):
            with st.expander(f"🎬 {video['topic']} - {video['timestamp'].strftime('%H:%M:%S')}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    if os.path.exists(video['path']):
                        st.video(video['path'])
                    else:
                        st.warning("Video file not found")
                with col2:
                    st.write(f"**Duration:** {video['duration']} seconds")
                    st.write(f"**Style:** Professional")
                    st.write(f"**Path:** `{video['path']}`")
                    
                    # Download button
                    if os.path.exists(video['path']):
                        with open(video['path'], "rb") as f:
                            st.download_button(
                                label="📥 Download",
                                data=f.read(),
                                file_name=os.path.basename(video['path']),
                                mime="video/mp4"
                            )
    else:
        st.info("No videos generated yet. Use Quick Generate to create your first video!")

# Main function
if __name__ == "__main__":
    render_video_generator()
