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
            ["Professional", "Casual", "Educational", "Entertainment", "Corporate", "Creative"],
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
    
    with col2:
        st.info("**Real Video Generation**")
        st.metric("Estimated Cost", "$0.00 (Local)")
        st.metric("Processing Time", "10-30 seconds")
        
        if st.button("🚀 Generate Real Video", type="primary", use_container_width=True):
            if video_topic:
                with st.spinner("🎬 Generating your real video..."):
                    # Generate actual video
                    video_path = generate_real_video(video_topic, video_style, video_length)
                    
                    if video_path and os.path.exists(video_path):
                        st.success("🎉 Your video is ready!")
                        
                        # Show video
                        st.video(video_path)
                        
                        # Video info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Duration", f"{video_length} seconds")
                        with col2:
                            st.metric("Quality", "720p")
                        with col3:
                            st.metric("Format", "MP4")
                        
                        # Download button
                        with open(video_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Video",
                                data=f.read(),
                                file_name=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
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
                            'duration': video_length
                        })
                    else:
                        st.error("❌ Video generation failed. Please try again.")
            else:
                st.warning("⚠️ Please enter a video topic")

def generate_real_video(topic, style, duration):
    """Generate a real video file using OpenCV"""
    if not OPENCV_AVAILABLE:
        st.error("OpenCV is not available. Cannot generate videos.")
        return None
        
    try:
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.mp4"
        video_path = os.path.join(output_dir, filename)
        
        # Video settings
        fps = 30
        width, height = 1280, 720
        total_frames = duration * fps
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        # Generate frames
        for frame_num in range(total_frames):
            # Create frame with topic text
            frame = create_video_frame(topic, style, frame_num, total_frames, width, height)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        
        return video_path
        
    except Exception as e:
        st.error(f"Error generating video: {str(e)}")
        return None

def create_video_frame(topic, style, frame_num, total_frames, width, height):
    """Create a single video frame"""
    # Create background
    if style == "Professional":
        bg_color = (50, 50, 100)  # Dark blue
    elif style == "Creative":
        bg_color = (100, 50, 100)  # Purple
    elif style == "Educational":
        bg_color = (50, 100, 50)  # Green
    else:
        bg_color = (80, 80, 80)  # Gray
    
    frame = np.full((height, width, 3), bg_color, dtype=np.uint8)
    
    # Add animated elements
    progress = frame_num / total_frames
    
    # Add topic text
    text = topic[:50] + "..." if len(topic) > 50 else topic
    cv2.putText(frame, text, (width//2 - 200, height//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Add style indicator
    cv2.putText(frame, f"Style: {style}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Add progress bar
    bar_width = int(width * 0.8)
    bar_height = 20
    bar_x = (width - bar_width) // 2
    bar_y = height - 100
    
    # Background bar
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                  (100, 100, 100), -1)
    
    # Progress bar
    progress_width = int(bar_width * progress)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), 
                  (0, 255, 0), -1)
    
    # Add frame counter
    cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (50, height - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Add some animation based on progress
    if progress > 0.5:
        # Add moving elements in second half
        offset = int(50 * np.sin(progress * 10))
        cv2.circle(frame, (width//2 + offset, height//2 - 100), 30, (255, 255, 0), -1)
    
    return frame

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
