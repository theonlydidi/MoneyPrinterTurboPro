"""
Video Utilities for MoneyPrinterTurboPro
Handles video processing, optimization, and GPU acceleration
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, ImageClip, ColorClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip
)
from moviepy.video.fx import resize, crop, fadein, fadeout

from app.core.config import settings
from app.core.logging import get_logger, time_operation
from app.models.video import VideoQuality, VideoStyle, VideoFormat


logger = get_logger(__name__)


class VideoUtils:
    """Video processing utilities with GPU acceleration"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_gpu_support()
        self._load_quality_presets()
        
    def _initialize_gpu_support(self):
        """Initialize GPU acceleration if available"""
        self.gpu_available = False
        
        try:
            # Check OpenCV GPU support
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                self.gpu_available = True
                self.logger.info("🚀 OpenCV GPU acceleration enabled")
        except Exception:
            pass
        
        try:
            # Check PyTorch GPU support
            import torch
            if torch.cuda.is_available():
                self.gpu_available = True
                self.logger.info(f"🚀 PyTorch GPU acceleration enabled: {torch.cuda.get_device_name(0)}")
        except ImportError:
            pass
    
    def _load_quality_presets(self):
        """Load video quality presets"""
        self.quality_presets = {
            VideoQuality.LOW: {
                'resolution': (854, 480),
                'fps': 30,
                'bitrate': '1000k',
                'codec': 'libx264',
                'preset': 'fast'
            },
            VideoQuality.MEDIUM: {
                'resolution': (1280, 720),
                'fps': 30,
                'bitrate': '2500k',
                'codec': 'libx264',
                'preset': 'medium'
            },
            VideoQuality.HIGH: {
                'resolution': (1920, 1080),
                'fps': 30,
                'bitrate': '5000k',
                'codec': 'libx264',
                'preset': 'slow'
            },
            VideoQuality.ULTRA: {
                'resolution': (3840, 2160),
                'fps': 60,
                'bitrate': '15000k',
                'codec': 'libx264',
                'preset': 'veryslow'
            }
        }
    
    @time_operation("video_optimization")
    async def optimize_video(
        self,
        video_path: str,
        quality: VideoQuality = VideoQuality.HIGH,
        target_size: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize video for target quality and size"""
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Get quality settings
            quality_settings = self.quality_presets.get(quality, self.quality_presets[VideoQuality.HIGH])
            
            # Resize video if needed
            if video.size != quality_settings['resolution']:
                video = self._resize_video(video, quality_settings['resolution'])
            
            # Adjust FPS if needed
            if video.fps != quality_settings['fps']:
                video = self._adjust_fps(video, quality_settings['fps'])
            
            # Generate output path
            if not output_path:
                timestamp = int(time.time())
                output_path = f"cache/optimized/optimized_{timestamp}.mp4"
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Export optimized video
            video.write_videofile(
                output_path,
                codec=quality_settings['codec'],
                preset=quality_settings['preset'],
                bitrate=quality_settings['bitrate'],
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            video.close()
            
            # Get output file size
            output_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'quality': quality.value,
                'resolution': quality_settings['resolution'],
                'fps': quality_settings['fps'],
                'bitrate': quality_settings['bitrate'],
                'output_size': output_size,
                'gpu_used': self.gpu_available
            }
            
        except Exception as e:
            self.logger.error(f"Video optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _resize_video(self, video: VideoFileClip, target_resolution: Tuple[int, int]) -> VideoFileClip:
        """Resize video to target resolution"""
        
        # Calculate aspect ratio
        current_ratio = video.size[0] / video.size[1]
        target_ratio = target_resolution[0] / target_resolution[1]
        
        if current_ratio > target_ratio:
            # Video is wider, crop horizontally
            new_width = int(video.size[1] * target_ratio)
            x_offset = (video.size[0] - new_width) // 2
            video = video.crop(x1=x_offset, y1=0, x2=x_offset + new_width, y2=video.size[1])
        elif current_ratio < target_ratio:
            # Video is taller, crop vertically
            new_height = int(video.size[0] / target_ratio)
            y_offset = (video.size[1] - new_height) // 2
            video = video.crop(x1=0, y1=y_offset, x2=video.size[0], y2=y_offset + new_height)
        
        # Resize to target resolution
        video = video.resize(target_resolution)
        
        return video
    
    def _adjust_fps(self, video: VideoFileClip, target_fps: int) -> VideoFileClip:
        """Adjust video FPS"""
        
        if video.fps != target_fps:
            # Use speedx to adjust FPS
            speed_factor = video.fps / target_fps
            video = video.speedx(speed_factor)
        
        return video
    
    @time_operation("video_thumbnail_generation")
    async def generate_thumbnail(
        self,
        video_path: str,
        timestamp: float = 0.0,
        size: Tuple[int, int] = (320, 180),
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate video thumbnail at specified timestamp"""
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Ensure timestamp is within video duration
            if timestamp >= video.duration:
                timestamp = video.duration / 2
            
            # Extract frame at timestamp
            frame = video.get_frame(timestamp)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            
            # Resize to target size
            pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)
            
            # Generate output path
            if not output_path:
                timestamp_str = str(int(timestamp)).replace('.', '_')
                output_path = f"cache/thumbnails/thumb_{timestamp_str}.jpg"
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save thumbnail
            pil_image.save(output_path, 'JPEG', quality=85)
            
            # Clean up
            video.close()
            
            return {
                'success': True,
                'thumbnail_path': output_path,
                'timestamp': timestamp,
                'size': size,
                'file_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_metadata_extraction")
    async def extract_metadata(
        self,
        video_path: str
    ) -> Dict[str, Any]:
        """Extract video metadata"""
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Get basic metadata
            metadata = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'audio_fps': video.audio.fps if video.audio else None,
                'nchannels': video.audio.nchannels if video.audio else None,
                'file_size': os.path.getsize(video_path),
                'codec': 'unknown',  # MoviePy doesn't provide codec info
                'bitrate': 'unknown'
            }
            
            # Clean up
            video.close()
            
            return {
                'success': True,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_concatenation")
    async def concatenate_videos(
        self,
        video_paths: List[str],
        output_path: Optional[str] = None,
        transition_duration: float = 0.5
    ) -> Dict[str, Any]:
        """Concatenate multiple videos with optional transitions"""
        
        try:
            if len(video_paths) < 2:
                raise ValueError("At least 2 videos required for concatenation")
            
            # Load all videos
            videos = []
            total_duration = 0.0
            
            for path in video_paths:
                video = VideoFileClip(path)
                videos.append(video)
                total_duration += video.duration
            
            # Apply transitions if specified
            if transition_duration > 0:
                videos_with_transitions = []
                
                for i, video in enumerate(videos):
                    if i > 0:
                        # Add fade out to previous video
                        videos_with_transitions[-1] = videos_with_transitions[-1].fadeout(transition_duration)
                    
                    if i < len(videos) - 1:
                        # Add fade in to current video
                        video = video.fadein(transition_duration)
                    
                    videos_with_transitions.append(video)
                
                videos = videos_with_transitions
            
            # Concatenate videos
            final_video = concatenate_videoclips(videos, method="compose")
            
            # Generate output path
            if not output_path:
                timestamp = int(time.time())
                output_path = f"cache/concatenated/concatenated_{timestamp}.mp4"
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Export concatenated video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            for video in videos:
                video.close()
            final_video.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'input_videos': len(video_paths),
                'total_duration': total_duration,
                'transition_duration': transition_duration,
                'output_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            self.logger.error(f"Video concatenation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_format_conversion")
    async def convert_format(
        self,
        video_path: str,
        target_format: VideoFormat,
        quality: VideoQuality = VideoQuality.HIGH,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert video to different format"""
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Get quality settings
            quality_settings = self.quality_presets.get(quality, self.quality_presets[VideoQuality.HIGH])
            
            # Generate output path
            if not output_path:
                timestamp = int(time.time())
                output_path = f"cache/converted/converted_{timestamp}.{target_format.value}"
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Determine codec based on format
            if target_format == VideoFormat.MP4:
                codec = 'libx264'
                audio_codec = 'aac'
            elif target_format == VideoFormat.MOV:
                codec = 'libx264'
                audio_codec = 'aac'
            elif target_format == VideoFormat.AVI:
                codec = 'libxvid'
                audio_codec = 'mp3'
            elif target_format == VideoFormat.WEBM:
                codec = 'libvpx'
                audio_codec = 'libvorbis'
            else:
                codec = 'libx264'
                audio_codec = 'aac'
            
            # Export converted video
            video.write_videofile(
                output_path,
                codec=codec,
                audio_codec=audio_codec,
                preset=quality_settings['preset'],
                bitrate=quality_settings['bitrate'],
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            video.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'target_format': target_format.value,
                'quality': quality.value,
                'output_size': os.path.getsize(output_path)
            }
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_quality_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available quality presets"""
        return {
            quality.value: {
                'name': quality.value.replace('_', ' ').title(),
                'description': f"{quality.value.replace('_', ' ').title()} quality preset",
                'resolution': config['resolution'],
                'fps': config['fps'],
                'bitrate': config['bitrate'],
                'codec': config['codec'],
                'preset': config['preset']
            }
            for quality, config in self.quality_presets.items()
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get supported video formats"""
        return [format.value for format in VideoFormat]
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """Get GPU acceleration status"""
        return {
            'gpu_available': self.gpu_available,
            'opencv_gpu': cv2.cuda.getCudaEnabledDeviceCount() > 0 if hasattr(cv2, 'cuda') else False
        }
    
    def calculate_optimal_settings(
        self,
        target_size_mb: int,
        duration_seconds: float,
        resolution: Tuple[int, int]
    ) -> Dict[str, Any]:
        """Calculate optimal video settings for target file size"""
        
        try:
            # Calculate target bitrate in bits per second
            target_size_bits = target_size_mb * 8 * 1024 * 1024
            target_bitrate = target_size_bits / duration_seconds
            
            # Convert to kbps
            target_bitrate_kbps = int(target_bitrate / 1000)
            
            # Calculate pixel count
            pixel_count = resolution[0] * resolution[1]
            
            # Estimate optimal bitrate based on resolution
            if pixel_count <= 480 * 854:  # 480p
                optimal_bitrate = max(800, target_bitrate_kbps)
            elif pixel_count <= 720 * 1280:  # 720p
                optimal_bitrate = max(1500, target_bitrate_kbps)
            elif pixel_count <= 1080 * 1920:  # 1080p
                optimal_bitrate = max(3000, target_bitrate_kbps)
            else:  # 4K+
                optimal_bitrate = max(8000, target_bitrate_kbps)
            
            # Determine codec preset based on target size
            if target_size_mb < 50:
                preset = 'ultrafast'
            elif target_size_mb < 200:
                preset = 'veryfast'
            elif target_size_mb < 500:
                preset = 'fast'
            else:
                preset = 'medium'
            
            return {
                'target_bitrate': target_bitrate_kbps,
                'optimal_bitrate': optimal_bitrate,
                'codec_preset': preset,
                'estimated_size_mb': (optimal_bitrate * 1000 * duration_seconds) / (8 * 1024 * 1024)
            }
            
        except Exception as e:
            self.logger.error(f"Optimal settings calculation failed: {str(e)}")
            return {
                'error': str(e),
                'fallback_bitrate': 2500,
                'fallback_preset': 'medium'
            }
