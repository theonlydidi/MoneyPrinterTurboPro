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
    
    with col2:
        st.info("**AI-Powered Video Generation**")
        st.metric("Estimated Cost", "$0.00 (Local)")
        st.metric("Processing Time", "15-45 seconds")
        
        if st.button("🚀 Generate AI Video", type="primary", use_container_width=True):
            if video_topic:
                with st.spinner("🤖 AI is generating your video content..."):
                    try:
                        # Import AI content generator
                        from app.services.ai_content_generator import get_ai_generator
                        
                        # Generate AI script
                        ai_gen = get_ai_generator()
                        script = ai_gen.generate_video_script(
                            topic=video_topic,
                            style=video_style,
                            duration=video_length,
                            target_audience=target_audience if 'target_audience' in locals() else "General",
                            language=language if 'language' in locals() else "English"
                        )
                        
                        # Store script in session state
                        st.session_state.ai_script = script
                        
                        st.success("✅ AI content generated successfully!")
                        
                        # Show script preview
                        with st.expander("📝 AI-Generated Script Preview", expanded=True):
                            st.json(script)
                        
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
