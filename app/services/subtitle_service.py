"""
Subtitle Service for MoneyPrinterTurboPro
Handles automatic subtitle generation, translation, and formatting
"""

import asyncio
import json
import os
import re
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import wave

import faster_whisper
import whisper
import speech_recognition as sr
from pydub import AudioSegment
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger, time_operation, log_api_request
from app.models.video import VideoRequest, VideoStyle


logger = get_logger(__name__)


class SubtitleService:
    """Subtitle generation and management service"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_providers()
        self._setup_directories()
        self._load_subtitle_styles()
        
    def _initialize_providers(self):
        """Initialize subtitle generation providers"""
        # Faster Whisper (local)
        try:
            self.faster_whisper_available = True
            # Initialize with appropriate model size
            model_size = "base"  # Can be: tiny, base, small, medium, large
            self.faster_whisper_model = faster_whisper.WhisperModel(
                model_size,
                device="cuda" if self._check_gpu_support() else "cpu",
                compute_type="float16" if self._check_gpu_support() else "float32"
            )
        except Exception as e:
            self.logger.warning(f"Faster Whisper not available: {str(e)}")
            self.faster_whisper_available = False
            
        # OpenAI Whisper (local)
        try:
            self.whisper_available = True
            self.whisper_model = whisper.load_model("base")
        except Exception as e:
            self.logger.warning(f"OpenAI Whisper not available: {str(e)}")
            self.whisper_available = False
            
        # Speech Recognition (Google)
        try:
            self.speech_recognition_available = True
            self.recognizer = sr.Recognizer()
        except Exception as e:
            self.logger.warning(f"Speech Recognition not available: {str(e)}")
            self.speech_recognition_available = False
            
        # Azure Speech Services
        if settings.api_keys.azure_speech_key and settings.api_keys.azure_speech_region:
            self.azure_speech_available = True
        else:
            self.azure_speech_available = False
            
        # Google Speech-to-Text
        if settings.api_keys.google_speech_key:
            self.google_speech_available = True
        else:
            self.google_speech_available = False
            
        self.logger.info(f"Subtitle Providers initialized: FasterWhisper={self.faster_whisper_available}, "
                        f"Whisper={self.whisper_available}, SpeechRecognition={self.speech_recognition_available}")
    
    def _check_gpu_support(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            import torch
            if torch.cuda.is_available():
                return True
        except ImportError:
            pass
        return False
    
    def _setup_directories(self):
        """Setup necessary directories"""
        directories = [
            settings.storage.temp_dir,
            "cache/subtitles",
            "cache/audio_segments",
            "output/subtitles"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_subtitle_styles(self):
        """Load subtitle styling presets"""
        self.subtitle_styles = {
            VideoStyle.PROFESSIONAL: {
                'font_family': 'Arial',
                'font_size': 24,
                'font_color': '#FFFFFF',
                'background_color': '#000000',
                'background_opacity': 0.7,
                'outline_color': '#000000',
                'outline_width': 2,
                'position': 'bottom',
                'margin': 20
            },
            VideoStyle.CREATIVE: {
                'font_family': 'Helvetica',
                'font_size': 28,
                'font_color': '#FFD700',
                'background_color': '#1E1E1E',
                'background_opacity': 0.8,
                'outline_color': '#FFD700',
                'outline_width': 3,
                'position': 'bottom',
                'margin': 25
            },
            VideoStyle.MINIMALIST: {
                'font_family': 'Roboto',
                'font_size': 20,
                'font_color': '#FFFFFF',
                'background_color': '#000000',
                'background_opacity': 0.5,
                'outline_color': '#FFFFFF',
                'outline_width': 1,
                'position': 'bottom',
                'margin': 15
            },
            VideoStyle.DYNAMIC: {
                'font_family': 'Impact',
                'font_size': 26,
                'font_color': '#00FF00',
                'background_color': '#000000',
                'background_opacity': 0.6,
                'outline_color': '#00FF00',
                'outline_width': 2,
                'position': 'bottom',
                'margin': 22
            },
            VideoStyle.CORPORATE: {
                'font_family': 'Calibri',
                'font_size': 22,
                'font_color': '#FFFFFF',
                'background_color': '#2F2F2F',
                'background_opacity': 0.8,
                'outline_color': '#2F2F2F',
                'outline_width': 2,
                'position': 'bottom',
                'margin': 18
            },
            VideoStyle.SOCIAL_MEDIA: {
                'font_family': 'Comic Sans MS',
                'font_size': 30,
                'font_color': '#FF6B6B',
                'background_color': '#FFFFFF',
                'background_opacity': 0.9,
                'outline_color': '#FF6B6B',
                'outline_width': 3,
                'position': 'bottom',
                'margin': 30
            },
            VideoStyle.EDUCATIONAL: {
                'font_family': 'Georgia',
                'font_size': 24,
                'font_color': '#2C3E50',
                'background_color': '#ECF0F1',
                'background_opacity': 0.9,
                'outline_color': '#2C3E50',
                'outline_width': 1,
                'position': 'bottom',
                'margin': 20
            },
            VideoStyle.ENTERTAINMENT: {
                'font_family': 'Bebas Neue',
                'font_size': 32,
                'font_color': '#FFD700',
                'background_color': '#000000',
                'background_opacity': 0.7,
                'outline_color': '#FFD700',
                'outline_width': 4,
                'position': 'bottom',
                'margin': 35
            }
        }
    
    @time_operation("subtitle_generation")
    async def generate_subtitles(
        self,
        audio_path: str,
        language: str = "en",
        provider: str = "auto",
        style: VideoStyle = VideoStyle.PROFESSIONAL,
        format: str = "srt",
        translate_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate subtitles from audio file"""
        
        try:
            # Validate input
            if not os.path.exists(audio_path):
                raise ValueError(f"Audio file not found: {audio_path}")
            
            # Select provider
            if provider == "auto":
                provider = self._select_best_provider(language, audio_path)
            
            # Generate subtitles
            result = await self._generate_with_provider(
                provider, audio_path, language, style
            )
            
            if result and result.get('success'):
                # Apply styling
                styled_subtitles = self._apply_subtitle_style(
                    result['subtitles'], style
                )
                
                # Export in requested format
                output_path = await self._export_subtitles(
                    styled_subtitles, format, style
                )
                
                # Translate if requested
                if translate_to and translate_to != language:
                    translated_result = await self._translate_subtitles(
                        styled_subtitles, language, translate_to
                    )
                    if translated_result['success']:
                        translated_output = await self._export_subtitles(
                            translated_result['subtitles'], format, style, suffix="_translated"
                        )
                        result['translated_path'] = translated_output
                
                return {
                    'success': True,
                    'subtitles': styled_subtitles,
                    'output_path': output_path,
                    'provider': provider,
                    'language': language,
                    'style': style.value,
                    'format': format,
                    'word_count': self._count_words(styled_subtitles),
                    'duration': result.get('duration', 0)
                }
            else:
                raise Exception(f"Subtitle generation failed with provider {provider}")
                
        except Exception as e:
            self.logger.error(f"Subtitle generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _select_best_provider(self, language: str, audio_path: str) -> str:
        """Select the best available provider based on language and audio"""
        
        # Check audio file size and duration
        try:
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0  # seconds
            file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
        except:
            duration = 0
            file_size = 0
        
        # Provider selection logic
        if language in ['en', 'es', 'fr', 'de', 'it', 'pt']:
            # Well-supported languages
            if self.faster_whisper_available and duration < 300:  # < 5 minutes
                return "faster_whisper"
            elif self.whisper_available and duration < 600:  # < 10 minutes
                return "whisper"
            elif self.azure_speech_available:
                return "azure"
            elif self.google_speech_available:
                return "google"
            else:
                return "speech_recognition"
        else:
            # Other languages
            if self.faster_whisper_available:
                return "faster_whisper"
            elif self.whisper_available:
                return "whisper"
            elif self.azure_speech_available:
                return "azure"
            else:
                return "speech_recognition"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_with_provider(
        self,
        provider: str,
        audio_path: str,
        language: str,
        style: VideoStyle
    ) -> Dict[str, Any]:
        """Generate subtitles with specific provider"""
        
        try:
            if provider == "faster_whisper":
                return await self._generate_faster_whisper(audio_path, language)
            elif provider == "whisper":
                return await self._generate_whisper(audio_path, language)
            elif provider == "azure":
                return await self._generate_azure(audio_path, language)
            elif provider == "google":
                return await self._generate_google(audio_path, language)
            elif provider == "speech_recognition":
                return await self._generate_speech_recognition(audio_path, language)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Provider {provider} subtitle generation failed: {str(e)}")
            raise
    
    async def _generate_faster_whisper(
        self,
        audio_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate subtitles using Faster Whisper"""
        
        try:
            # Transcribe audio
            segments, info = self.faster_whisper_model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                vad_filter=True
            )
            
            # Convert to subtitle format
            subtitles = []
            for segment in segments:
                start_time = segment.start
                end_time = segment.end
                text = segment.text.strip()
                
                if text:  # Only add non-empty segments
                    subtitles.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text,
                        'words': segment.words if hasattr(segment, 'words') else []
                    })
            
            return {
                'success': True,
                'subtitles': subtitles,
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration
            }
            
        except Exception as e:
            raise Exception(f"Faster Whisper generation failed: {str(e)}")
    
    async def _generate_whisper(
        self,
        audio_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate subtitles using OpenAI Whisper"""
        
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True
            )
            
            # Convert to subtitle format
            subtitles = []
            for segment in result['segments']:
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()
                
                if text:  # Only add non-empty segments
                    subtitles.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text,
                        'words': segment.get('words', [])
                    })
            
            return {
                'success': True,
                'subtitles': subtitles,
                'language': result.get('language', language),
                'duration': result.get('duration', 0)
            }
            
        except Exception as e:
            raise Exception(f"Whisper generation failed: {str(e)}")
    
    async def _generate_azure(
        self,
        audio_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate subtitles using Azure Speech Services"""
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.api_keys.azure_speech_key,
                region=settings.api_keys.azure_speech_region
            )
            speech_config.speech_recognition_language = language
            
            # Create audio config
            audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
            
            # Create recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )
            
            # Transcribe audio
            subtitles = []
            done = False
            
            def handle_result(evt):
                if evt.result.text:
                    subtitles.append({
                        'start': evt.result.offset / 10000000,  # Convert to seconds
                        'end': (evt.result.offset + evt.result.duration) / 10000000,
                        'text': evt.result.text.strip()
                    })
            
            def stop_cb(evt):
                nonlocal done
                done = True
            
            recognizer.recognized.connect(handle_result)
            recognizer.session_stopped.connect(stop_cb)
            recognizer.canceled.connect(stop_cb)
            
            # Start recognition
            recognizer.start_continuous_recognition()
            
            # Wait for completion
            while not done:
                await asyncio.sleep(0.1)
            
            recognizer.stop_continuous_recognition()
            
            return {
                'success': True,
                'subtitles': subtitles,
                'language': language
            }
            
        except Exception as e:
            raise Exception(f"Azure subtitle generation failed: {str(e)}")
    
    async def _generate_google(
        self,
        audio_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate subtitles using Google Speech-to-Text"""
        
        try:
            # Google Speech-to-Text API call
            url = "https://speech.googleapis.com/v1/speech:recognize"
            headers = {
                "Authorization": f"Bearer {settings.api_keys.google_speech_key}",
                "Content-Type": "application/json"
            }
            
            # Read and encode audio file
            with open(audio_path, 'rb') as audio_file:
                audio_content = audio_file.read()
                audio_encoded = requests.utils.quote(audio_content)
            
            data = {
                "config": {
                    "encoding": "MP3",
                    "sampleRateHertz": 16000,
                    "languageCode": language,
                    "enableWordTimeOffsets": True,
                    "enableAutomaticPunctuation": True
                },
                "audio": {
                    "content": audio_encoded
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                subtitles = []
                
                for result_item in result.get('results', []):
                    for alternative in result_item.get('alternatives', []):
                        text = alternative.get('transcript', '').strip()
                        if text:
                            # Calculate timing (Google doesn't provide word-level timing in this format)
                            subtitles.append({
                                'start': 0,  # Placeholder
                                'end': 0,    # Placeholder
                                'text': text
                            })
                
                return {
                    'success': True,
                    'subtitles': subtitles,
                    'language': language
                }
            else:
                raise Exception(f"Google Speech-to-Text API error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Google subtitle generation failed: {str(e)}")
    
    async def _generate_speech_recognition(
        self,
        audio_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate subtitles using Speech Recognition"""
        
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)
            
            # Convert to WAV format for speech recognition
            wav_path = audio_path.replace('.', '_temp.')
            audio.export(wav_path, format='wav')
            
            # Read audio file
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(
                audio_data,
                language=language
            )
            
            # Clean up temporary file
            try:
                os.remove(wav_path)
            except:
                pass
            
            # Create simple subtitle (no timing information)
            subtitles = [{
                'start': 0,
                'end': len(audio) / 1000.0,  # Duration in seconds
                'text': text
            }]
            
            return {
                'success': True,
                'subtitles': subtitles,
                'language': language
            }
            
        except Exception as e:
            raise Exception(f"Speech Recognition generation failed: {str(e)}")
    
    def _apply_subtitle_style(
        self,
        subtitles: List[Dict[str, Any]],
        style: VideoStyle
    ) -> List[Dict[str, Any]]:
        """Apply styling to subtitles"""
        
        style_config = self.subtitle_styles.get(style, self.subtitle_styles[VideoStyle.PROFESSIONAL])
        
        styled_subtitles = []
        for subtitle in subtitles:
            styled_subtitle = subtitle.copy()
            styled_subtitle['style'] = style_config
            styled_subtitles.append(styled_subtitle)
        
        return styled_subtitles
    
    async def _export_subtitles(
        self,
        subtitles: List[Dict[str, Any]],
        format: str,
        style: VideoStyle,
        suffix: str = ""
    ) -> str:
        """Export subtitles in specified format"""
        
        timestamp = int(time.time())
        output_path = f"cache/subtitles/subtitles_{timestamp}{suffix}.{format}"
        
        if format == "srt":
            content = self._export_srt(subtitles)
        elif format == "vtt":
            content = self._export_vtt(subtitles)
        elif format == "ass":
            content = self._export_ass(subtitles, style)
        elif format == "json":
            content = json.dumps(subtitles, indent=2)
        else:
            raise ValueError(f"Unsupported subtitle format: {format}")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _export_srt(self, subtitles: List[Dict[str, Any]]) -> str:
        """Export subtitles in SRT format"""
        
        srt_content = ""
        for i, subtitle in enumerate(subtitles, 1):
            start_time = self._format_time(subtitle['start'])
            end_time = self._format_time(subtitle['end'])
            text = subtitle['text']
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        return srt_content
    
    def _export_vtt(self, subtitles: List[Dict[str, Any]]) -> str:
        """Export subtitles in VTT format"""
        
        vtt_content = "WEBVTT\n\n"
        for subtitle in subtitles:
            start_time = self._format_time_vtt(subtitle['start'])
            end_time = self._format_time_vtt(subtitle['end'])
            text = subtitle['text']
            
            vtt_content += f"{start_time} --> {end_time}\n"
            vtt_content += f"{text}\n\n"
        
        return vtt_content
    
    def _export_ass(self, subtitles: List[Dict[str, Any]], style: VideoStyle) -> str:
        """Export subtitles in ASS format with styling"""
        
        style_config = self.subtitle_styles.get(style, self.subtitle_styles[VideoStyle.PROFESSIONAL])
        
        ass_content = "[Script Info]\n"
        ass_content += "Title: Generated Subtitles\n"
        ass_content += "ScriptType: v4.00+\n\n"
        
        ass_content += "[V4+ Styles]\n"
        ass_content += "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        
        # Create style
        style_name = f"Style{style.value.title()}"
        font_family = style_config['font_family']
        font_size = style_config['font_size']
        primary_color = self._hex_to_ass_color(style_config['font_color'])
        outline_color = self._hex_to_ass_color(style_config['outline_color'])
        outline_width = style_config['outline_width']
        margin_v = style_config['margin']
        
        ass_content += f"{style_name}, {font_family}, {font_size}, {primary_color}, &H00FFFFFF, {outline_color}, &H80000000, 0, 0, 0, 0, 100, 100, 0, 0, 1, {outline_width}, 0, 2, 10, 10, {margin_v}, 1\n\n"
        
        ass_content += "[Events]\n"
        ass_content += "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        
        for subtitle in subtitles:
            start_time = self._format_time_ass(subtitle['start'])
            end_time = self._format_time_ass(subtitle['end'])
            text = subtitle['text']
            
            ass_content += f"Dialogue: 0, {start_time}, {end_time}, {style_name}, , 0, 0, 0, , {text}\n"
        
        return ass_content
    
    def _format_time(self, seconds: float) -> str:
        """Format time in SRT format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """Format time in VTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def _format_time_ass(self, seconds: float) -> str:
        """Format time in ASS format (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def _hex_to_ass_color(self, hex_color: str) -> str:
        """Convert hex color to ASS color format"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # ASS uses BGR format with alpha
        return f"&H00{b:02X}{g:02X}{r:02X}"
    
    async def _translate_subtitles(
        self,
        subtitles: List[Dict[str, Any]],
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Translate subtitles to target language"""
        
        try:
            # Simple translation using basic mapping (for demonstration)
            # In production, you'd use a proper translation service
            translation_map = {
                'en': {
                    'es': {
                        'hello': 'hola',
                        'world': 'mundo',
                        'video': 'video',
                        'generation': 'generación'
                    },
                    'fr': {
                        'hello': 'bonjour',
                        'world': 'monde',
                        'video': 'vidéo',
                        'generation': 'génération'
                    }
                }
            }
            
            translated_subtitles = []
            for subtitle in subtitles:
                translated_text = subtitle['text']
                
                # Apply translation if available
                if (source_language in translation_map and 
                    target_language in translation_map[source_language]):
                    for source_word, target_word in translation_map[source_language][target_language].items():
                        translated_text = translated_text.replace(source_word, target_word)
                
                translated_subtitle = subtitle.copy()
                translated_subtitle['text'] = translated_text
                translated_subtitle['translated_language'] = target_language
                translated_subtitles.append(translated_subtitle)
            
            return {
                'success': True,
                'subtitles': translated_subtitles,
                'source_language': source_language,
                'target_language': target_language
            }
            
        except Exception as e:
            self.logger.error(f"Subtitle translation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _count_words(self, subtitles: List[Dict[str, Any]]) -> int:
        """Count total words in subtitles"""
        total_words = 0
        for subtitle in subtitles:
            words = subtitle['text'].split()
            total_words += len(words)
        return total_words
    
    @time_operation("subtitle_batch_generation")
    async def generate_batch_subtitles(
        self,
        audio_files: List[str],
        language: str = "en",
        provider: str = "auto",
        style: VideoStyle = VideoStyle.PROFESSIONAL,
        format: str = "srt"
    ) -> Dict[str, Any]:
        """Generate subtitles for multiple audio files"""
        
        try:
            results = []
            total_duration = 0.0
            total_words = 0
            
            for i, audio_path in enumerate(audio_files):
                self.logger.info(f"Processing audio file {i+1}/{len(audio_files)}")
                
                result = await self.generate_subtitles(
                    audio_path, language, provider, style, format
                )
                
                if result['success']:
                    results.append(result)
                    total_duration += result.get('duration', 0)
                    total_words += result.get('word_count', 0)
                else:
                    self.logger.error(f"Failed to generate subtitles for file {i+1}: {result['error']}")
                    results.append({
                        'success': False,
                        'error': result['error'],
                        'file_index': i
                    })
            
            # Calculate success rate
            successful = sum(1 for r in results if r['success'])
            success_rate = (successful / len(results)) * 100 if results else 0
            
            return {
                'success': success_rate > 0,
                'results': results,
                'total_files': len(audio_files),
                'successful_files': successful,
                'success_rate': success_rate,
                'total_duration': total_duration,
                'total_words': total_words,
                'provider': provider,
                'language': language,
                'style': style.value
            }
            
        except Exception as e:
            self.logger.error(f"Batch subtitle generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_available_formats(self) -> List[str]:
        """Get available subtitle export formats"""
        return ["srt", "vtt", "ass", "json"]
    
    def get_subtitle_styles(self) -> Dict[str, Dict[str, Any]]:
        """Get available subtitle styles"""
        return {
            style.value: {
                'name': style.value.replace('_', ' ').title(),
                'description': f"{style.value.replace('_', ' ').title()} subtitle style",
                'config': config
            }
            for style, config in self.subtitle_styles.items()
        }
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all subtitle providers"""
        status = {}
        
        providers = {
            'faster_whisper': self.faster_whisper_available,
            'whisper': self.whisper_available,
            'speech_recognition': self.speech_recognition_available,
            'azure': self.azure_speech_available,
            'google': self.google_speech_available
        }
        
        for provider, available in providers.items():
            status[provider] = {
                'available': available,
                'status': 'active' if available else 'unavailable',
                'supported_languages': self._get_provider_languages(provider),
                'last_check': datetime.now().isoformat()
            }
        
        return status
    
    def _get_provider_languages(self, provider: str) -> List[str]:
        """Get supported languages for provider"""
        language_map = {
            'faster_whisper': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
            'whisper': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
            'speech_recognition': ['en', 'es', 'fr', 'de', 'it', 'pt'],
            'azure': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar'],
            'google': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
        }
        
        return language_map.get(provider, ['en'])
