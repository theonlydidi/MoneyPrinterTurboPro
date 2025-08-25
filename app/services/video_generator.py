"""
Video Generator Service for MoneyPrinterTurboPro
Orchestrates the entire video generation process
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ImageClip
from moviepy.video.fx import resize, crop, fadein, fadeout
import cv2
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger, time_operation
from app.models.video import VideoRequest, VideoResponse, VideoTemplate, VideoBatchRequest, VideoAnalytics
from app.services.ai_service import AIService
from app.services.voice_service import VoiceService
from app.services.subtitle_service import SubtitleService
from app.services.music_service import MusicService
from app.services.effects_service import EffectsService
from app.services.storage_service import StorageManager
from app.services.database_service import DatabaseService
from app.services.monitoring_service import MonitoringService
from app.utils.video_utils import VideoUtils


logger = get_logger(__name__)


class VideoGeneratorService:
    """Main video generation orchestration service"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_services()
        self._setup_directories()
        self._load_generation_config()
        
    def _initialize_services(self):
        """Initialize all required services"""
        try:
            self.ai_service = AIService()
            self.voice_service = VoiceService()
            self.subtitle_service = SubtitleService()
            self.music_service = MusicService()
            self.effects_service = EffectsService()
            self.storage_manager = StorageManager()
            self.database_service = DatabaseService()
            self.monitoring_service = MonitoringService()
            self.video_utils = VideoUtils()
            
            self.logger.info("🚀 All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Service initialization failed: {str(e)}")
            raise
    
    def _setup_directories(self):
        """Setup working directories"""
        directories = [
            "cache/temp",
            "cache/audio",
            "cache/videos",
            "cache/images",
            "cache/thumbnails",
            "output/videos",
            "output/audio",
            "output/images"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_generation_config(self):
        """Load video generation configuration"""
        self.generation_config = {
            'max_concurrent_generations': settings.performance.max_concurrent_generations,
            'default_fps': 30,
            'default_resolution': (1920, 1080),
            'audio_sample_rate': 44100,
            'temp_file_cleanup': True,
            'quality_presets': settings.quality_presets,
            'style_presets': settings.style_presets
        }
    
    @time_operation("video_generation")
    async def generate_video(
        self,
        request: VideoRequest,
        user_id: Optional[str] = None,
        template_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a complete video from request"""
        
        start_time = time.time()
        generation_id = f"gen_{int(time.time())}_{user_id or 'anonymous'}"
        
        try:
            self.logger.info(f"🎬 Starting video generation: {generation_id}")
            
            # Save request to database
            db_result = await self.database_service.save_video_request(request, user_id)
            if not db_result['success']:
                raise Exception(f"Failed to save video request: {db_result.get('error')}")
            
            request_id = db_result['request_id']
            
            # Update status to processing
            await self.database_service.update_video_status(request_id, "processing")
            
            # Step 1: Generate script using AI
            self.logger.info(f"🤖 Generating script for video {generation_id}")
            script_result = await self.ai_service.generate_script(request, user_id)
            
            if not script_result['success']:
                await self.database_service.update_video_status(request_id, "failed", metadata={'error': script_result['error']})
                raise Exception(f"Script generation failed: {script_result['error']}")
            
            script = script_result['script']
            self.logger.info(f"✅ Script generated successfully: {len(script)} characters")
            
            # Step 2: Generate voice synthesis
            self.logger.info(f"🎤 Generating voice synthesis for video {generation_id}")
            voice_result = await self.voice_service.synthesize_speech(
                script,
                request.voice_preset,
                quality="high" if request.quality == "ultra" else "medium"
            )
            
            if not voice_result['success']:
                await self.database_service.update_video_status(request_id, "failed", metadata={'error': voice_result['error']})
                raise Exception(f"Voice synthesis failed: {voice_result['error']}")
            
            audio_path = voice_result['audio_path']
            audio_duration = voice_result['duration']
            self.logger.info(f"✅ Voice synthesis completed: {audio_duration:.2f}s")
            
            # Step 3: Generate subtitles if requested
            subtitle_path = None
            if request.include_subtitles:
                self.logger.info(f"📝 Generating subtitles for video {generation_id}")
                subtitle_result = await self.subtitle_service.generate_subtitles(
                    audio_path,
                    request.language,
                    style=request.style
                )
                
                if subtitle_result['success']:
                    subtitle_path = subtitle_result['output_path']
                    self.logger.info(f"✅ Subtitles generated successfully")
                else:
                    self.logger.warning(f"Subtitle generation failed: {subtitle_result['error']}")
            
            # Step 4: Select background music
            music_path = None
            if request.background_music:
                self.logger.info(f"🎵 Selecting background music for video {generation_id}")
                music_result = await self.music_service.select_background_music(
                    request.style,
                    audio_duration,
                    request.music_intensity
                )
                
                if music_result['success']:
                    music_path = music_result['music_path']
                    self.logger.info(f"✅ Background music selected: {music_result['source']}")
                else:
                    self.logger.warning(f"Music selection failed: {music_result['error']}")
            
            # Step 5: Create video composition
            self.logger.info(f"🎬 Creating video composition for {generation_id}")
            video_result = await self._create_video_composition(
                script,
                audio_path,
                subtitle_path,
                music_path,
                request,
                generation_id
            )
            
            if not video_result['success']:
                await self.database_service.update_video_status(request_id, "failed", metadata={'error': video_result['error']})
                raise Exception(f"Video composition failed: {video_result['error']}")
            
            video_path = video_result['video_path']
            video_duration = video_result['duration']
            video_size = video_result['size']
            
            # Step 6: Apply video effects
            self.logger.info(f"✨ Applying video effects for {generation_id}")
            effects_result = await self.effects_service.apply_video_effects(
                video_result['video_clip'],
                request.style
            )
            
            if effects_result['success']:
                # Re-render with effects
                final_video_path = await self._render_final_video(
                    effects_result['processed_video_clip'],
                    generation_id,
                    request.quality
                )
                video_path = final_video_path
                video_size = os.path.getsize(final_video_path)
                self.logger.info(f"✅ Video effects applied successfully")
            else:
                self.logger.warning(f"Video effects failed: {effects_result['error']}")
            
            # Step 7: Optimize video
            self.logger.info(f"🔧 Optimizing video for {generation_id}")
            optimization_result = await self.video_utils.optimize_video(
                video_path,
                request.quality
            )
            
            if optimization_result['success']:
                video_path = optimization_result['output_path']
                video_size = optimization_result['output_size']
                self.logger.info(f"✅ Video optimization completed")
            else:
                self.logger.warning(f"Video optimization failed: {optimization_result['error']}")
            
            # Step 8: Generate thumbnail
            thumbnail_path = None
            try:
                thumbnail_result = await self.video_utils.generate_thumbnail(video_path)
                if thumbnail_result['success']:
                    thumbnail_path = thumbnail_result['output_path']
                    self.logger.info(f"✅ Thumbnail generated successfully")
            except Exception as e:
                self.logger.warning(f"Thumbnail generation failed: {str(e)}")
            
            # Step 9: Upload to storage
            self.logger.info(f"📤 Uploading video to storage for {generation_id}")
            storage_result = await self.storage_manager.upload_file(
                video_path,
                f"videos/{generation_id}.mp4",
                metadata={
                    'user_id': user_id,
                    'template_id': template_id,
                    'style': request.style.value,
                    'quality': request.quality.value,
                    'duration': video_duration,
                    'size': video_size,
                    'generated_at': datetime.now().isoformat()
                }
            )
            
            if not storage_result['success']:
                self.logger.warning(f"Storage upload failed: {storage_result['error']}")
            
            # Step 10: Update database with final status
            final_metadata = {
                'video_path': video_path,
                'thumbnail_path': thumbnail_path,
                'audio_path': audio_path,
                'subtitle_path': subtitle_path,
                'music_path': music_path,
                'final_duration': video_duration,
                'final_size': video_size,
                'generation_time': time.time() - start_time,
                'storage_url': storage_result.get('url', ''),
                'script_length': len(script),
                'audio_duration': audio_duration
            }
            
            await self.database_service.update_video_status(
                request_id,
                "completed",
                video_path=video_path,
                metadata=final_metadata
            )
            
            # Record metrics
            generation_time = time.time() - start_time
            self.monitoring_service.record_video_generation(
                "completed",
                request.style.value,
                request.quality.value,
                generation_time,
                video_size
            )
            
            # Create response
            response = VideoResponse(
                request_id=request_id,
                status="completed",
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                duration=video_duration,
                size=video_size,
                generation_time=generation_time,
                metadata=final_metadata
            )
            
            self.logger.info(f"🎉 Video generation completed successfully: {generation_id}")
            
            return {
                'success': True,
                'response': response,
                'generation_id': generation_id,
                'generation_time': generation_time
            }
            
        except Exception as e:
            self.logger.error(f"Video generation failed for {generation_id}: {str(e)}")
            
            # Update database status
            if 'request_id' in locals():
                await self.database_service.update_video_status(
                    request_id,
                    "failed",
                    metadata={'error': str(e), 'error_type': type(e).__name__}
                )
            
            # Record metrics
            generation_time = time.time() - start_time
            self.monitoring_service.record_video_generation(
                "failed",
                request.style.value if hasattr(request, 'style') else 'unknown',
                request.quality.value if hasattr(request, 'quality') else 'unknown',
                generation_time,
                0
            )
            
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'generation_id': generation_id,
                'generation_time': generation_time
            }
        
        finally:
            # Cleanup temporary files
            if self.generation_config['temp_file_cleanup']:
                await self._cleanup_temp_files(generation_id)
    
    async def _create_video_composition(
        self,
        script: str,
        audio_path: str,
        subtitle_path: Optional[str],
        music_path: Optional[str],
        request: VideoRequest,
        generation_id: str
    ) -> Dict[str, Any]:
        """Create the main video composition"""
        
        try:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create video dimensions
            if request.aspect_ratio == "16:9":
                video_size = (1920, 1080)
            elif request.aspect_ratio == "9:16":
                video_size = (1080, 1920)
            elif request.aspect_ratio == "4:3":
                video_size = (1440, 1080)
            else:  # 1:1
                video_size = (1080, 1080)
            
            # Create background (simple gradient for now)
            background = self._create_background(video_size, request.style)
            
            # Create text clips for script
            text_clips = self._create_text_clips(script, duration, video_size, request.style)
            
            # Combine all elements
            video_clips = [background] + text_clips
            
            # Add music if available
            if music_path and os.path.exists(music_path):
                music_clip = AudioFileClip(music_path)
                # Loop music if needed
                if music_clip.duration < duration:
                    loops_needed = int(duration / music_clip.duration) + 1
                    music_clip = music_clip.loop(loops_needed)
                
                # Trim to exact duration
                music_clip = music_clip.subclip(0, duration)
                
                # Mix audio
                final_audio = CompositeVideoClip([audio_clip, music_clip.volumex(0.3)])
            else:
                final_audio = audio_clip
            
            # Create final composition
            final_video = CompositeVideoClip(video_clips, size=video_size)
            final_video = final_video.set_duration(duration)
            final_video = final_video.set_audio(final_audio)
            
            # Render video
            output_path = f"cache/temp/{generation_id}_composition.mp4"
            final_video.write_videofile(
                output_path,
                fps=self.generation_config['default_fps'],
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'video_path': output_path,
                'video_clip': final_video,
                'duration': duration,
                'size': file_size
            }
            
        except Exception as e:
            raise Exception(f"Video composition creation failed: {str(e)}")
    
    def _create_background(self, size: tuple, style: VideoStyle) -> VideoFileClip:
        """Create background for video"""
        
        try:
            # Create a simple gradient background
            width, height = size
            
            # Create gradient based on style
            if style == VideoStyle.PROFESSIONAL:
                # Professional blue gradient
                gradient = np.zeros((height, width, 3), dtype=np.uint8)
                for y in range(height):
                    factor = y / height
                    gradient[y, :] = [
                        int(25 + (50 - 25) * factor),  # Blue
                        int(50 + (100 - 50) * factor), # Green
                        int(100 + (200 - 100) * factor) # Red
                    ]
            
            elif style == VideoStyle.CREATIVE:
                # Creative colorful gradient
                gradient = np.zeros((height, width, 3), dtype=np.uint8)
                for y in range(height):
                    factor = y / height
                    gradient[y, :] = [
                        int(100 + (200 - 100) * factor), # Red
                        int(50 + (150 - 50) * factor),   # Green
                        int(150 + (250 - 150) * factor)  # Blue
                    ]
            
            elif style == VideoStyle.MINIMALIST:
                # Minimalist white to light gray
                gradient = np.zeros((height, width, 3), dtype=np.uint8)
                for y in range(height):
                    factor = y / height
                    color = int(240 + (220 - 240) * factor)
                    gradient[y, :] = [color, color, color]
            
            else:
                # Default gradient
                gradient = np.zeros((height, width, 3), dtype=np.uint8)
                for y in range(height):
                    factor = y / height
                    gradient[y, :] = [
                        int(50 + (100 - 50) * factor),
                        int(100 + (150 - 100) * factor),
                        int(150 + (200 - 150) * factor)
                    ]
            
            # Save gradient as image
            temp_path = "cache/temp/background.png"
            cv2.imwrite(temp_path, gradient)
            
            # Create video clip from image
            background = ImageClip(temp_path).set_duration(1)
            
            return background
            
        except Exception as e:
            # Fallback to solid color
            solid_color = np.full((height, width, 3), [100, 150, 200], dtype=np.uint8)
            temp_path = "cache/temp/background_fallback.png"
            cv2.imwrite(temp_path, solid_color)
            return ImageClip(temp_path).set_duration(1)
    
    def _create_text_clips(
        self,
        script: str,
        duration: float,
        video_size: tuple,
        style: VideoStyle
    ) -> List[TextClip]:
        """Create text clips from script"""
        
        try:
            # Split script into sentences
            sentences = script.split('. ')
            if not sentences[-1].endswith('.'):
                sentences[-1] += '.'
            
            # Calculate timing
            sentence_duration = duration / len(sentences)
            
            text_clips = []
            width, height = video_size
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    # Create text clip
                    text_clip = TextClip(
                        sentence.strip(),
                        fontsize=40 if style == VideoStyle.MINIMALIST else 50,
                        color='white' if style == VideoStyle.MINIMALIST else 'yellow',
                        font='Arial-Bold',
                        size=(width * 0.8, None),
                        method='caption'
                    )
                    
                    # Position text
                    text_clip = text_clip.set_position('center')
                    
                    # Set timing
                    start_time = i * sentence_duration
                    end_time = (i + 1) * sentence_duration
                    text_clip = text_clip.set_start(start_time).set_end(end_time)
                    
                    # Add fade effects
                    text_clip = text_clip.fadein(0.5).fadeout(0.5)
                    
                    text_clips.append(text_clip)
            
            return text_clips
            
        except Exception as e:
            # Fallback: single text clip
            fallback_clip = TextClip(
                script[:100] + "..." if len(script) > 100 else script,
                fontsize=40,
                color='white',
                font='Arial',
                size=(width * 0.8, None),
                method='caption'
            ).set_position('center').set_duration(duration)
            
            return [fallback_clip]
    
    async def _render_final_video(
        self,
        video_clip: VideoFileClip,
        generation_id: str,
        quality: VideoQuality
    ) -> str:
        """Render final video with effects"""
        
        try:
            output_path = f"cache/temp/{generation_id}_final.mp4"
            
            # Get quality settings
            quality_settings = self.generation_config['quality_presets'].get(quality, {})
            
            video_clip.write_videofile(
                output_path,
                fps=quality_settings.get('fps', self.generation_config['default_fps']),
                codec=quality_settings.get('codec', 'libx264'),
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Final video rendering failed: {str(e)}")
    
    async def _cleanup_temp_files(self, generation_id: str):
        """Clean up temporary files"""
        
        try:
            temp_patterns = [
                f"cache/temp/{generation_id}_*",
                "cache/temp/background*.png",
                "cache/temp/temp-audio.m4a"
            ]
            
            for pattern in temp_patterns:
                for file_path in Path("cache/temp").glob(pattern.split("/")[-1]):
                    try:
                        file_path.unlink()
                    except Exception as e:
                        self.logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")
            
        except Exception as e:
            self.logger.warning(f"Temp file cleanup failed: {str(e)}")
    
    @time_operation("batch_video_generation")
    async def generate_batch_videos(
        self,
        batch_request: VideoBatchRequest,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate multiple videos in batch"""
        
        try:
            self.logger.info(f"🎬 Starting batch video generation: {len(batch_request.requests)} videos")
            
            # Limit concurrent generations
            max_concurrent = min(
                len(batch_request.requests),
                self.generation_config['max_concurrent_generations']
            )
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def generate_single_video(request: VideoRequest):
                async with semaphore:
                    return await self.generate_video(request, user_id)
            
            # Generate all videos concurrently
            tasks = [generate_single_video(req) for req in batch_request.requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful = []
            failed = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed.append({
                        'index': i,
                        'error': str(result),
                        'error_type': type(result).__name__
                    })
                elif result['success']:
                    successful.append(result)
                else:
                    failed.append({
                        'index': i,
                        'error': result.get('error', 'Unknown error'),
                        'error_type': result.get('error_type', 'Unknown')
                    })
            
            return {
                'success': True,
                'total_requested': len(batch_request.requests),
                'successful': len(successful),
                'failed': len(failed),
                'results': {
                    'successful': successful,
                    'failed': failed
                }
            }
            
        except Exception as e:
            self.logger.error(f"Batch video generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def get_generation_status(self, request_id: int) -> Dict[str, Any]:
        """Get video generation status"""
        
        try:
            result = await self.database_service.get_video_request(request_id)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get generation status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def cancel_generation(self, request_id: int) -> Dict[str, Any]:
        """Cancel video generation"""
        
        try:
            # Update status to cancelled
            result = await self.database_service.update_video_status(request_id, "cancelled")
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Video generation cancelled successfully'
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to cancel generation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        
        try:
            return {
                'ai_service': 'available',
                'voice_service': 'available',
                'subtitle_service': 'available',
                'music_service': 'available',
                'effects_service': 'available',
                'storage_manager': self.storage_manager.get_storage_status(),
                'database_service': self.database_service.get_database_status(),
                'monitoring_service': self.monitoring_service.get_metrics_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get service status: {str(e)}")
            return {
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def close(self):
        """Close all services"""
        
        try:
            await self.database_service.close()
            await self.monitoring_service.close()
            self.logger.info("Video generator service closed")
            
        except Exception as e:
            self.logger.error(f"Failed to close video generator service: {str(e)}")
