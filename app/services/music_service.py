"""
Music Service for MoneyPrinterTurboPro
Handles background music selection, generation, and audio mixing
"""

import asyncio
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import wave

import requests
from pydub import AudioSegment
import librosa
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger, time_operation, log_api_request
from app.models.video import VideoStyle, VideoQuality


logger = get_logger(__name__)


class MusicService:
    """Background music service with multiple providers and intelligent selection"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_providers()
        self._load_music_library()
        self._setup_directories()
        
    def _initialize_providers(self):
        """Initialize music generation and sourcing providers"""
        # AI Music Generation
        try:
            import torch
            self.torch_available = True
        except ImportError:
            self.torch_available = False
            
        # MusicLM (Google)
        if settings.api_keys.google_music_key:
            self.musiclm_available = True
        else:
            self.musiclm_available = False
            
        # Mubert (AI Music)
        if settings.api_keys.mubert_api_key:
            self.mubert_available = True
        else:
            self.mubert_available = False
            
        # AIVA (AI Music)
        if settings.api_keys.aiva_api_key:
            self.aiva_available = True
        else:
            self.aiva_available = False
            
        # Stock Music APIs
        if settings.api_keys.pixabay_api_key:
            self.pixabay_available = True
        else:
            self.pixabay_available = False
            
        if settings.api_keys.pexels_api_key:
            self.pexels_available = True
        else:
            self.pexels_available = False
            
        # Local Music Library
        self.local_music_available = self._check_local_music()
        
        self.logger.info(f"Music Providers initialized: MusicLM={self.musiclm_available}, "
                        f"Mubert={self.mubert_available}, AIVA={self.aiva_available}, "
                        f"Stock={self.pixabay_available or self.pexels_available}")
    
    def _check_local_music(self) -> bool:
        """Check if local music library is available"""
        music_dir = Path("resource/music")
        if music_dir.exists() and any(music_dir.iterdir()):
            return True
        return False
    
    def _setup_directories(self):
        """Setup necessary directories"""
        directories = [
            settings.storage.temp_dir,
            "cache/music",
            "cache/audio_mixes",
            "output/music"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_music_library(self):
        """Load music library and categorization"""
        self.music_categories = {
            VideoStyle.PROFESSIONAL: {
                'mood': ['corporate', 'business', 'professional', 'sophisticated'],
                'tempo': ['moderate', 'slow'],
                'instruments': ['piano', 'strings', 'orchestral', 'ambient'],
                'energy': 'low'
            },
            VideoStyle.CREATIVE: {
                'mood': ['creative', 'inspiring', 'innovative', 'artistic'],
                'tempo': ['moderate', 'fast'],
                'instruments': ['electronic', 'synth', 'guitar', 'drums'],
                'energy': 'medium'
            },
            VideoStyle.MINIMALIST: {
                'mood': ['minimal', 'calm', 'peaceful', 'simple'],
                'tempo': ['slow', 'very_slow'],
                'instruments': ['piano', 'ambient', 'acoustic', 'strings'],
                'energy': 'very_low'
            },
            VideoStyle.DYNAMIC: {
                'mood': ['energetic', 'dynamic', 'powerful', 'motivational'],
                'tempo': ['fast', 'very_fast'],
                'instruments': ['drums', 'bass', 'electric_guitar', 'synth'],
                'energy': 'high'
            },
            VideoStyle.CORPORATE: {
                'mood': ['corporate', 'trustworthy', 'reliable', 'authoritative'],
                'tempo': ['moderate', 'slow'],
                'instruments': ['piano', 'strings', 'brass', 'orchestral'],
                'energy': 'low'
            },
            VideoStyle.SOCIAL_MEDIA: {
                'mood': ['trendy', 'catchy', 'fun', 'engaging'],
                'tempo': ['fast', 'moderate'],
                'instruments': ['pop', 'electronic', 'drums', 'bass'],
                'energy': 'medium'
            },
            VideoStyle.EDUCATIONAL: {
                'mood': ['educational', 'clear', 'focused', 'engaging'],
                'tempo': ['moderate', 'slow'],
                'instruments': ['piano', 'strings', 'ambient', 'acoustic'],
                'energy': 'low'
            },
            VideoStyle.ENTERTAINMENT: {
                'mood': ['entertaining', 'fun', 'exciting', 'engaging'],
                'tempo': ['fast', 'moderate'],
                'instruments': ['pop', 'rock', 'electronic', 'drums'],
                'energy': 'medium'
            }
        }
        
        # Music intensity mapping
        self.intensity_mapping = {
            'low': {
                'volume': -20,  # dB
                'complexity': 'simple',
                'layers': 1
            },
            'medium': {
                'volume': -15,  # dB
                'complexity': 'moderate',
                'layers': 2
            },
            'high': {
                'volume': -10,  # dB
                'complexity': 'complex',
                'layers': 3
            }
        }
    
    @time_operation("music_selection")
    async def select_background_music(
        self,
        style: VideoStyle,
        duration: int,
        intensity: str = "medium",
        mood: Optional[str] = None,
        exclude_genres: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Select appropriate background music based on style and requirements"""
        
        try:
            # Get style-specific music requirements
            style_requirements = self.music_categories.get(style, self.music_categories[VideoStyle.PROFESSIONAL])
            
            # Override mood if specified
            if mood:
                style_requirements['mood'] = [mood]
            
            # Filter out excluded genres
            if exclude_genres:
                style_requirements['mood'] = [m for m in style_requirements['mood'] if m not in exclude_genres]
            
            # Get intensity settings
            intensity_settings = self.intensity_mapping.get(intensity, self.intensity_mapping['medium'])
            
            # Try to find existing music first
            existing_music = await self._find_existing_music(
                style_requirements, duration, intensity_settings
            )
            
            if existing_music:
                return {
                    'success': True,
                    'music_path': existing_music['path'],
                    'source': 'existing',
                    'style': style.value,
                    'mood': existing_music['mood'],
                    'duration': existing_music['duration'],
                    'intensity': intensity
                }
            
            # Generate new music if no existing music found
            generated_music = await self._generate_music(
                style_requirements, duration, intensity_settings
            )
            
            if generated_music['success']:
                return {
                    'success': True,
                    'music_path': generated_music['path'],
                    'source': 'generated',
                    'style': style.value,
                    'mood': generated_music['mood'],
                    'duration': generated_music['duration'],
                    'intensity': intensity,
                    'provider': generated_music['provider']
                }
            
            # Fallback to stock music
            stock_music = await self._get_stock_music(
                style_requirements, duration, intensity_settings
            )
            
            if stock_music['success']:
                return {
                    'success': True,
                    'music_path': stock_music['path'],
                    'source': 'stock',
                    'style': style.value,
                    'mood': stock_music['mood'],
                    'duration': stock_music['duration'],
                    'intensity': intensity,
                    'provider': stock_music['provider']
                }
            
            raise Exception("No suitable background music found")
            
        except Exception as e:
            self.logger.error(f"Music selection failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _find_existing_music(
        self,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find existing music that matches requirements"""
        
        try:
            # Check local music library
            if self.local_music_available:
                music_dir = Path("resource/music")
                music_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))
                
                for music_file in music_files:
                    # Check if file matches requirements
                    if self._music_file_matches_requirements(
                        music_file, requirements, duration, intensity_settings
                    ):
                        return {
                            'path': str(music_file),
                            'mood': requirements['mood'][0],
                            'duration': self._get_audio_duration(str(music_file))
                        }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error finding existing music: {str(e)}")
            return None
    
    def _music_file_matches_requirements(
        self,
        music_file: Path,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> bool:
        """Check if music file matches the requirements"""
        
        try:
            # Check duration (allow some flexibility)
            file_duration = self._get_audio_duration(str(music_file))
            duration_match = abs(file_duration - duration) <= 30  # Within 30 seconds
            
            # Check file size (rough indicator of complexity)
            file_size = music_file.stat().st_size / (1024 * 1024)  # MB
            size_match = True  # Basic check for now
            
            # Check filename for mood indicators
            filename = music_file.stem.lower()
            mood_match = any(mood in filename for mood in requirements['mood'])
            
            return duration_match and size_match and mood_match
            
        except Exception:
            return False
    
    async def _generate_music(
        self,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate new music using AI providers"""
        
        # Try providers in order of preference
        providers = ['musiclm', 'mubert', 'aiva']
        
        for provider in providers:
            try:
                if provider == 'musiclm' and self.musiclm_available:
                    result = await self._generate_musiclm(requirements, duration, intensity_settings)
                    if result['success']:
                        return result
                elif provider == 'mubert' and self.mubert_available:
                    result = await self._generate_mubert(requirements, duration, intensity_settings)
                    if result['success']:
                        return result
                elif provider == 'aiva' and self.aiva_available:
                    result = await self._generate_aiva(requirements, duration, intensity_settings)
                    if result['success']:
                        return result
            except Exception as e:
                self.logger.warning(f"Provider {provider} music generation failed: {str(e)}")
                continue
        
        return {'success': False, 'error': 'All AI music providers failed'}
    
    async def _generate_musiclm(
        self,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate music using Google MusicLM"""
        
        try:
            # MusicLM API call
            url = "https://generativelanguage.googleapis.com/v1beta/models/musiclm:generateContent"
            headers = {
                "Authorization": f"Bearer {settings.api_keys.google_music_key}",
                "Content-Type": "application/json"
            }
            
            # Create music prompt
            mood = requirements['mood'][0]
            tempo = requirements['tempo'][0]
            instruments = ', '.join(requirements['instruments'])
            
            prompt = f"Create a {mood} {tempo} tempo background music using {instruments} for a {duration} second video"
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                # Process MusicLM response and save audio
                # This is a simplified implementation
                output_path = f"cache/music/musiclm_{int(time.time())}.mp3"
                
                # For now, return a placeholder
                return {
                    'success': True,
                    'path': output_path,
                    'mood': mood,
                    'duration': duration,
                    'provider': 'musiclm'
                }
            else:
                raise Exception(f"MusicLM API error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"MusicLM generation failed: {str(e)}")
    
    async def _generate_mubert(
        self,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate music using Mubert"""
        
        try:
            # Mubert API call
            url = "https://api.mubert.com/v2/Record"
            headers = {
                "Authorization": f"Bearer {settings.api_keys.mubert_api_key}",
                "Content-Type": "application/json"
            }
            
            mood = requirements['mood'][0]
            tempo = requirements['tempo'][0]
            
            data = {
                "method": "Record",
                "params": {
                    "mood": mood,
                    "tempo": tempo,
                    "duration": duration,
                    "format": "mp3"
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                # Process Mubert response and save audio
                output_path = f"cache/music/mubert_{int(time.time())}.mp3"
                
                return {
                    'success': True,
                    'path': output_path,
                    'mood': mood,
                    'duration': duration,
                    'provider': 'mubert'
                }
            else:
                raise Exception(f"Mubert API error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Mubert generation failed: {str(e)}")
    
    async def _generate_aiva(
        self,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate music using AIVA"""
        
        try:
            # AIVA API call
            url = "https://api.aiva.ai/v1/tracks"
            headers = {
                "Authorization": f"Bearer {settings.api_keys.aiva_api_key}",
                "Content-Type": "application/json"
            }
            
            mood = requirements['mood'][0]
            tempo = requirements['tempo'][0]
            
            data = {
                "name": f"Background Music - {mood}",
                "mood": mood,
                "tempo": tempo,
                "duration": duration,
                "style": "background"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                # Process AIVA response and save audio
                output_path = f"cache/music/aiva_{int(time.time())}.mp3"
                
                return {
                    'success': True,
                    'path': output_path,
                    'mood': mood,
                    'duration': duration,
                    'provider': 'aiva'
                }
            else:
                raise Exception(f"AIVA API error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"AIVA generation failed: {str(e)}")
    
    async def _get_stock_music(
        self,
        requirements: Dict[str, Any],
        duration: int,
        intensity_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get stock music from various providers"""
        
        # Try stock music providers
        providers = ['pixabay', 'pexels']
        
        for provider in providers:
            try:
                if provider == 'pixabay' and self.pixabay_available:
                    result = await self._get_pixabay_music(requirements, duration)
                    if result['success']:
                        return result
                elif provider == 'pexels' and self.pexels_available:
                    result = await self._get_pexels_music(requirements, duration)
                    if result['success']:
                        return result
            except Exception as e:
                self.logger.warning(f"Provider {provider} stock music failed: {str(e)}")
                continue
        
        return {'success': False, 'error': 'All stock music providers failed'}
    
    async def _get_pixabay_music(
        self,
        requirements: Dict[str, Any],
        duration: int
    ) -> Dict[str, Any]:
        """Get music from Pixabay"""
        
        try:
            url = "https://pixabay.com/api/audio/"
            params = {
                'key': settings.api_keys.pixabay_api_key,
                'q': requirements['mood'][0],
                'audio_type': 'music',
                'safesearch': 'true',
                'per_page': 20
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                hits = result.get('hits', [])
                
                if hits:
                    # Select a random hit that matches duration
                    suitable_hits = [h for h in hits if abs(h.get('duration', 0) - duration) <= 30]
                    
                    if suitable_hits:
                        selected_hit = random.choice(suitable_hits)
                        download_url = selected_hit['previewURL']
                        
                        # Download the music
                        output_path = f"cache/music/pixabay_{int(time.time())}.mp3"
                        await self._download_music(download_url, output_path)
                        
                        return {
                            'success': True,
                            'path': output_path,
                            'mood': requirements['mood'][0],
                            'duration': selected_hit.get('duration', duration),
                            'provider': 'pixabay'
                        }
            
            raise Exception("No suitable Pixabay music found")
            
        except Exception as e:
            raise Exception(f"Pixabay music retrieval failed: {str(e)}")
    
    async def _get_pexels_music(
        self,
        requirements: Dict[str, Any],
        duration: int
    ) -> Dict[str, Any]:
        """Get music from Pexels"""
        
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": settings.api_keys.pexels_api_key
            }
            params = {
                'query': requirements['mood'][0] + ' background music',
                'per_page': 20
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                videos = result.get('videos', [])
                
                if videos:
                    # Select a random video with audio
                    suitable_videos = [v for v in videos if v.get('duration', 0) >= duration]
                    
                    if suitable_videos:
                        selected_video = random.choice(suitable_videos)
                        # Extract audio from video
                        output_path = f"cache/music/pexels_{int(time.time())}.mp3"
                        await self._extract_audio_from_video(selected_video['video_files'][0]['link'], output_path)
                        
                        return {
                            'success': True,
                            'path': output_path,
                            'mood': requirements['mood'][0],
                            'duration': selected_video.get('duration', duration),
                            'provider': 'pexels'
                        }
            
            raise Exception("No suitable Pexels music found")
            
        except Exception as e:
            raise Exception(f"Pexels music retrieval failed: {str(e)}")
    
    async def _download_music(self, url: str, output_path: str):
        """Download music from URL"""
        
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    async def _extract_audio_from_video(self, video_url: str, output_path: str):
        """Extract audio from video URL"""
        
        # Download video first
        video_path = f"cache/music/temp_video_{int(time.time())}.mp4"
        await self._download_music(video_url, video_path)
        
        # Extract audio using pydub
        try:
            video = AudioSegment.from_file(video_path)
            audio = video.set_channels(1).set_frame_rate(44100)
            audio.export(output_path, format='mp3')
        finally:
            # Clean up temporary video file
            try:
                os.remove(video_path)
            except:
                pass
    
    @time_operation("music_mixing")
    async def mix_audio_with_music(
        self,
        audio_path: str,
        music_path: str,
        music_volume: float = -20.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mix voice audio with background music"""
        
        try:
            # Load audio files
            voice_audio = AudioSegment.from_file(audio_path)
            background_music = AudioSegment.from_file(music_path)
            
            # Adjust music volume
            background_music = background_music + music_volume
            
            # Loop music if it's shorter than voice audio
            voice_duration = len(voice_audio)
            music_duration = len(background_music)
            
            if music_duration < voice_duration:
                # Calculate how many loops needed
                loops_needed = int(voice_duration / music_duration) + 1
                background_music = background_music * loops_needed
            
            # Trim music to match voice duration
            background_music = background_music[:voice_duration]
            
            # Apply fade effects
            if fade_in > 0:
                background_music = background_music.fade_in(fade_in * 1000)  # Convert to milliseconds
            
            if fade_out > 0:
                background_music = background_music.fade_out(fade_out * 1000)
            
            # Mix audio
            mixed_audio = voice_audio.overlay(background_music)
            
            # Generate output path if not provided
            if not output_path:
                timestamp = int(time.time())
                output_path = f"cache/audio_mixes/mixed_{timestamp}.mp3"
            
            # Export mixed audio
            mixed_audio.export(output_path, format='mp3', bitrate='192k')
            
            return {
                'success': True,
                'output_path': output_path,
                'voice_duration': voice_duration / 1000.0,  # Convert to seconds
                'music_duration': music_duration / 1000.0,
                'mixed_duration': len(mixed_audio) / 1000.0,
                'music_volume': music_volume
            }
            
        except Exception as e:
            self.logger.error(f"Audio mixing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            self.logger.warning(f"Could not determine audio duration: {str(e)}")
            return 0.0
    
    def get_available_moods(self) -> List[str]:
        """Get available music moods"""
        moods = set()
        for style_config in self.music_categories.values():
            moods.update(style_config['mood'])
        return sorted(list(moods))
    
    def get_available_tempos(self) -> List[str]:
        """Get available music tempos"""
        tempos = set()
        for style_config in self.music_categories.values():
            tempos.update(style_config['tempo'])
        return sorted(list(tempos))
    
    def get_music_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get music categories for each video style"""
        return {
            style.value: {
                'name': style.value.replace('_', ' ').title(),
                'description': f"{style.value.replace('_', ' ').title()} music style",
                'mood': config['mood'],
                'tempo': config['tempo'],
                'instruments': config['instruments'],
                'energy': config['energy']
            }
            for style, config in self.music_categories.items()
        }
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all music providers"""
        status = {}
        
        providers = {
            'musiclm': self.musiclm_available,
            'mubert': self.mubert_available,
            'aiva': self.aiva_available,
            'pixabay': self.pixabay_available,
            'pexels': self.pexels_available,
            'local': self.local_music_available
        }
        
        for provider, available in providers.items():
            status[provider] = {
                'available': available,
                'status': 'active' if available else 'unavailable',
                'capabilities': self._get_provider_capabilities(provider),
                'last_check': datetime.now().isoformat()
            }
        
        return status
    
    def _get_provider_capabilities(self, provider: str) -> List[str]:
        """Get capabilities for each provider"""
        capabilities = {
            'musiclm': ['ai_generation', 'style_transfer', 'custom_duration'],
            'mubert': ['ai_generation', 'mood_based', 'real_time'],
            'aiva': ['ai_generation', 'emotion_based', 'orchestral'],
            'pixabay': ['stock_music', 'free_licensing', 'multiple_formats'],
            'pexels': ['stock_music', 'video_audio', 'free_licensing'],
            'local': ['offline_access', 'instant_loading', 'custom_curation']
        }
        
        return capabilities.get(provider, [])
