"""
Effects Service for MoneyPrinterTurboPro
Handles video effects, transitions, filters, and animations
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from moviepy import (
    VideoFileClip, ImageClip, ColorClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip
)
from moviepy.video.fx import (
    resize, crop, fadein, fadeout, slide_in, slide_out,
    rotate, mirror_x, mirror_y, speedx, colorx
)
from moviepy.video.tools.subtitles import SubtitlesClip

from app.core.config import settings
from app.core.logging import get_logger, time_operation, log_api_request
from app.models.video import VideoStyle, VideoQuality, TransitionType


logger = get_logger(__name__)


class EffectsService:
    """Video effects and transitions service with GPU acceleration"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_gpu_support()
        self._load_effect_presets()
        self._setup_directories()
        
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
    
    def _setup_directories(self):
        """Setup necessary directories"""
        directories = [
            settings.storage.temp_dir,
            "cache/effects",
            "cache/transitions",
            "output/effects"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_effect_presets(self):
        """Load effect presets for different video styles"""
        self.effect_presets = {
            VideoStyle.PROFESSIONAL: {
                'transitions': ['fade', 'slide'],
                'filters': ['enhance', 'color_correction'],
                'animations': ['subtle_zoom', 'gentle_pan'],
                'intensity': 'low'
            },
            VideoStyle.CREATIVE: {
                'transitions': ['zoom', 'rotate', 'slide'],
                'filters': ['artistic', 'color_shift'],
                'animations': ['dynamic_zoom', 'creative_pan'],
                'intensity': 'high'
            },
            VideoStyle.MINIMALIST: {
                'transitions': ['fade', 'simple_slide'],
                'filters': ['clean', 'minimal'],
                'animations': ['subtle_movement'],
                'intensity': 'very_low'
            },
            VideoStyle.DYNAMIC: {
                'transitions': ['fast_slide', 'zoom', 'wipe'],
                'filters': ['vibrant', 'high_contrast'],
                'animations': ['rapid_zoom', 'dynamic_pan'],
                'intensity': 'very_high'
            }
        }
    
    @time_operation("video_effects_application")
    async def apply_video_effects(
        self,
        video_path: str,
        style: VideoStyle,
        effects_config: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply video effects based on style and configuration"""
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Get style-specific effects
            style_effects = self.effect_presets.get(style, self.effect_presets[VideoStyle.PROFESSIONAL])
            
            # Merge with custom effects config
            if effects_config:
                style_effects = {**style_effects, **effects_config}
            
            # Apply filters
            if 'filters' in style_effects:
                video = await self._apply_filters(video, style_effects['filters'])
            
            # Apply animations
            if 'animations' in style_effects:
                video = await self._apply_animations(video, style_effects['animations'])
            
            # Generate output path
            if not output_path:
                timestamp = int(time.time())
                output_path = f"cache/effects/effects_{timestamp}.mp4"
            
            # Export video with effects
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
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
                'style': style.value,
                'effects_applied': list(style_effects.keys()),
                'gpu_used': self.gpu_available
            }
            
        except Exception as e:
            self.logger.error(f"Video effects application failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _apply_filters(self, video: VideoFileClip, filters: List[str]) -> VideoFileClip:
        """Apply video filters"""
        
        try:
            for filter_name in filters:
                if filter_name == 'enhance':
                    video = self._enhance_filter(video)
                elif filter_name == 'color_correction':
                    video = self._color_correction_filter(video)
                elif filter_name == 'artistic':
                    video = self._artistic_filter(video)
                elif filter_name == 'clean':
                    video = self._clean_filter(video)
                elif filter_name == 'vibrant':
                    video = self._vibrant_filter(video)
            
            return video
            
        except Exception as e:
            self.logger.error(f"Filter application failed: {str(e)}")
            return video
    
    def _enhance_filter(self, video: VideoFileClip) -> VideoFileClip:
        """Apply enhancement filter"""
        def enhance_frame(frame):
            pil_image = Image.fromarray(frame)
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.1)
            return np.array(pil_image)
        
        return video.fl_image(enhance_frame)
    
    def _color_correction_filter(self, video: VideoFileClip) -> VideoFileClip:
        """Apply color correction filter"""
        def color_correct_frame(frame):
            pil_image = Image.fromarray(frame)
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(1.05)
            return np.array(pil_image)
        
        return video.fl_image(color_correct_frame)
    
    def _artistic_filter(self, video: VideoFileClip) -> VideoFileClip:
        """Apply artistic filter"""
        def artistic_frame(frame):
            pil_image = Image.fromarray(frame)
            pil_image = pil_image.filter(ImageFilter.EDGE_ENHANCE)
            pil_image = pil_image.filter(ImageFilter.EMBOSS)
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(1.5)
            return np.array(pil_image)
        
        return video.fl_image(artistic_frame)
    
    def _clean_filter(self, video: VideoFileClip) -> VideoFileClip:
        """Apply clean filter"""
        def clean_frame(frame):
            pil_image = Image.fromarray(frame)
            pil_image = pil_image.filter(ImageFilter.SMOOTH)
            pil_image = pil_image.filter(ImageFilter.MedianFilter(size=3))
            return np.array(pil_image)
        
        return video.fl_image(clean_frame)
    
    def _vibrant_filter(self, video: VideoFileClip) -> VideoFileClip:
        """Apply vibrant filter"""
        def vibrant_frame(frame):
            pil_image = Image.fromarray(frame)
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(1.8)
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.4)
            return np.array(pil_image)
        
        return video.fl_image(vibrant_frame)
    
    async def _apply_animations(self, video: VideoFileClip, animations: List[str]) -> VideoFileClip:
        """Apply video animations"""
        
        try:
            for animation_name in animations:
                if animation_name == 'subtle_zoom':
                    video = self._subtle_zoom_animation(video)
                elif animation_name == 'gentle_pan':
                    video = self._gentle_pan_animation(video)
                elif animation_name == 'dynamic_zoom':
                    video = self._dynamic_zoom_animation(video)
                elif animation_name == 'creative_pan':
                    video = self._creative_pan_animation(video)
                elif animation_name == 'subtle_movement':
                    video = self._subtle_movement_animation(video)
                elif animation_name == 'rapid_zoom':
                    video = self._rapid_zoom_animation(video)
                elif animation_name == 'dynamic_pan':
                    video = self._dynamic_pan_animation(video)
            
            return video
            
        except Exception as e:
            self.logger.error(f"Animation application failed: {str(e)}")
            return video
    
    def _subtle_zoom_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply subtle zoom animation"""
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            zoom_factor = 1 + 0.05 * math.sin(t * 2 * math.pi / video.duration)
            return resize(frame, zoom_factor)
        
        return video.fl(zoom_effect)
    
    def _gentle_pan_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply gentle pan animation"""
        def pan_effect(get_frame, t):
            frame = get_frame(t)
            pan_x = 0.02 * math.sin(t * math.pi / video.duration)
            pan_y = 0.01 * math.cos(t * math.pi / video.duration)
            return frame[int(pan_y * frame.shape[0]):, int(pan_x * frame.shape[1]):]
        
        return video.fl(pan_effect)
    
    def _dynamic_zoom_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply dynamic zoom animation"""
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            zoom_factor = 1 + 0.15 * math.sin(t * 4 * math.pi / video.duration)
            return resize(frame, zoom_factor)
        
        return video.fl(zoom_effect)
    
    def _creative_pan_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply creative pan animation"""
        def pan_effect(get_frame, t):
            frame = get_frame(t)
            pan_x = 0.05 * math.sin(t * 3 * math.pi / video.duration)
            pan_y = 0.03 * math.cos(t * 2 * math.pi / video.duration)
            return frame[int(pan_y * frame.shape[0]):, int(pan_x * frame.shape[1]):]
        
        return video.fl(pan_effect)
    
    def _subtle_movement_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply subtle movement animation"""
        def movement_effect(get_frame, t):
            frame = get_frame(t)
            move_x = 0.01 * math.sin(t * math.pi / video.duration)
            move_y = 0.005 * math.cos(t * math.pi / video.duration)
            return frame[int(move_y * frame.shape[0]):, int(move_x * frame.shape[1]):]
        
        return video.fl(movement_effect)
    
    def _rapid_zoom_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply rapid zoom animation"""
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            zoom_factor = 1 + 0.25 * math.sin(t * 8 * math.pi / video.duration)
            return resize(frame, zoom_factor)
        
        return video.fl(zoom_effect)
    
    def _dynamic_pan_animation(self, video: VideoFileClip) -> VideoFileClip:
        """Apply dynamic pan animation"""
        def pan_effect(get_frame, t):
            frame = get_frame(t)
            pan_x = 0.08 * math.sin(t * 5 * math.pi / video.duration)
            pan_y = 0.06 * math.cos(t * 4 * math.pi / video.duration)
            return frame[int(pan_y * frame.shape[0]):, int(pan_x * frame.shape[1]):]
        
        return video.fl(pan_effect)
    
    def get_available_effects(self) -> Dict[str, Dict[str, Any]]:
        """Get available effects for each style"""
        return {
            style.value: {
                'transitions': config['transitions'],
                'filters': config['filters'],
                'animations': config['animations'],
                'intensity': config['intensity']
            }
            for style, config in self.effect_presets.items()
        }
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """Get GPU acceleration status"""
        return {
            'gpu_available': self.gpu_available,
            'opencv_gpu': cv2.cuda.getCudaEnabledDeviceCount() > 0 if hasattr(cv2, 'cuda') else False
        }
