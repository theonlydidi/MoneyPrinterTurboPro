"""
Voice Service for MoneyPrinterTurboPro
Handles text-to-speech with multiple providers and voice customization
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import wave

import edge_tts
import azure.cognitiveservices.speech as speechsdk
from elevenlabs import generate, save, set_api_key
import requests
from pydub import AudioSegment
import librosa
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger, time_operation, log_api_request
from app.models.video import VoicePreset, AudioFormat


logger = get_logger(__name__)


class VoiceService:
    """Voice synthesis service with multiple providers"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_providers()
        self._load_voice_presets()
        self._setup_directories()
        
    def _initialize_providers(self):
        """Initialize TTS providers with API keys"""
        # Edge TTS (Microsoft) - Always available
        self.edge_available = True
        
        # Azure Speech
        if settings.api_keys.azure_speech_key and settings.api_keys.azure_speech_region:
            self.azure_available = True
            self.azure_speech_config = speechsdk.SpeechConfig(
                subscription=settings.api_keys.azure_speech_key,
                region=settings.api_keys.azure_speech_region
            )
        else:
            self.azure_available = False
            
        # ElevenLabs
        if settings.api_keys.elevenlabs_api_key:
            set_api_key(settings.api_keys.elevenlabs_api_key)
            self.elevenlabs_available = True
        else:
            self.elevenlabs_available = False
            
        # Google Text-to-Speech
        if settings.api_keys.google_tts_key:
            self.google_tts_available = True
        else:
            self.google_tts_available = False
            
        # Coqui TTS (Local)
        try:
            import TTS
            self.coqui_available = True
        except ImportError:
            self.coqui_available = False
            
        self.logger.info(f"Voice Providers initialized: Edge={self.edge_available}, "
                        f"Azure={self.azure_available}, ElevenLabs={self.elevenlabs_available}")
    
    def _load_voice_presets(self):
        """Load voice presets for different styles"""
        self.voice_presets = {
            VoicePreset.MALE_1: {
                'edge_tts': 'en-US-DavisNeural',
                'azure': 'en-US-DavisNeural',
                'elevenlabs': 'pNInz6obpgDQGcFmaJgB',  # Adam
                'style': 'professional',
                'rate': '+0%',
                'volume': '+0%'
            },
            VoicePreset.MALE_2: {
                'edge_tts': 'en-US-JennyNeural',
                'azure': 'en-US-JennyNeural',
                'elevenlabs': 'EXAVITQu4vr4xnSDxMaL',  # Bella
                'style': 'friendly',
                'rate': '+0%',
                'volume': '+0%'
            },
            VoicePreset.FEMALE_1: {
                'edge_tts': 'en-US-AriaNeural',
                'azure': 'en-US-AriaNeural',
                'elevenlabs': '21m00Tcm4TlvDq8ikWAM',  # Rachel
                'style': 'professional',
                'rate': '+0%',
                'volume': '+0%'
            },
            VoicePreset.FEMALE_2: {
                'edge_tts': 'en-US-SaraNeural',
                'azure': 'en-US-SaraNeural',
                'elevenlabs': 'AZnzlk1XvdvUeBnXmlld',  # Domi
                'style': 'energetic',
                'rate': '+0%',
                'volume': '+0%'
            },
            VoicePreset.NEUTRAL: {
                'edge_tts': 'en-US-GuyNeural',
                'azure': 'en-US-GuyNeural',
                'elevenlabs': 'pNInz6obpgDQGcFmaJgB',  # Adam
                'style': 'neutral',
                'rate': '+0%',
                'volume': '+0%'
            },
            VoicePreset.EXCITED: {
                'edge_tts': 'en-US-JennyNeural',
                'azure': 'en-US-JennyNeural',
                'elevenlabs': 'EXAVITQu4vr4xnSDxMaL',  # Bella
                'style': 'excited',
                'rate': '+10%',
                'volume': '+10%'
            },
            VoicePreset.CALM: {
                'edge_tts': 'en-US-AriaNeural',
                'azure': 'en-US-AriaNeural',
                'elevenlabs': '21m00Tcm4TlvDq8ikWAM',  # Rachel
                'style': 'calm',
                'rate': '-10%',
                'volume': '-5%'
            },
            VoicePreset.PROFESSIONAL: {
                'edge_tts': 'en-US-DavisNeural',
                'azure': 'en-US-DavisNeural',
                'elevenlabs': 'pNInz6obpgDQGcFmaJgB',  # Adam
                'style': 'professional',
                'rate': '+0%',
                'volume': '+0%'
            }
        }
    
    def _setup_directories(self):
        """Setup necessary directories"""
        directories = [
            settings.storage.temp_dir,
            "cache/audio",
            "cache/voice",
            "output/audio"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @time_operation("voice_synthesis")
    async def synthesize_speech(
        self,
        text: str,
        voice_preset: VoicePreset = VoicePreset.PROFESSIONAL,
        provider: str = "auto",
        output_format: AudioFormat = AudioFormat.MP3,
        quality: str = "high"
    ) -> Dict[str, Any]:
        """Synthesize speech from text"""
        
        try:
            # Validate input
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")
            
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Select provider
            if provider == "auto":
                provider = self._select_best_provider(voice_preset, quality)
            
            # Get voice configuration
            voice_config = self.voice_presets.get(voice_preset, self.voice_presets[VoicePreset.PROFESSIONAL])
            
            # Generate speech
            result = await self._synthesize_with_provider(
                provider, cleaned_text, voice_config, output_format, quality
            )
            
            if result and result.get('success'):
                # Post-process audio if needed
                if quality == "ultra":
                    result = await self._enhance_audio_quality(result)
                
                return {
                    'success': True,
                    'audio_path': result['audio_path'],
                    'duration': result['duration'],
                    'provider': provider,
                    'voice_preset': voice_preset.value,
                    'format': output_format.value,
                    'quality': quality,
                    'file_size': os.path.getsize(result['audio_path']) if result['audio_path'] else 0
                }
            else:
                raise Exception(f"Voice synthesis failed with provider {provider}")
                
        except Exception as e:
            self.logger.error(f"Voice synthesis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for TTS"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Handle common abbreviations
        abbreviations = {
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Dr.': 'Doctor',
            'Prof.': 'Professor',
            'vs.': 'versus',
            'etc.': 'et cetera',
            'i.e.': 'that is',
            'e.g.': 'for example'
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def _select_best_provider(self, voice_preset: VoicePreset, quality: str) -> str:
        """Select the best available provider based on quality and voice preset"""
        
        # Quality-based provider selection
        if quality == "ultra":
            # Prefer high-quality providers
            if self.elevenlabs_available:
                return "elevenlabs"
            elif self.azure_available:
                return "azure"
            elif self.edge_available:
                return "edge_tts"
        
        elif quality == "high":
            # Balanced quality and speed
            if self.azure_available:
                return "azure"
            elif self.edge_available:
                return "edge_tts"
            elif self.elevenlabs_available:
                return "elevenlabs"
        
        else:
            # Standard quality, prioritize speed
            if self.edge_available:
                return "edge_tts"
            elif self.azure_available:
                return "azure"
            elif self.elevenlabs_available:
                return "elevenlabs"
        
        # Fallback to edge_tts (always available)
        return "edge_tts"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _synthesize_with_provider(
        self,
        provider: str,
        text: str,
        voice_config: Dict[str, Any],
        output_format: AudioFormat,
        quality: str
    ) -> Dict[str, Any]:
        """Synthesize speech with specific provider"""
        
        try:
            if provider == "edge_tts":
                return await self._synthesize_edge_tts(text, voice_config, output_format)
            elif provider == "azure":
                return await self._synthesize_azure(text, voice_config, output_format)
            elif provider == "elevenlabs":
                return await self._synthesize_elevenlabs(text, voice_config, output_format, quality)
            elif provider == "google_tts":
                return await self._synthesize_google_tts(text, voice_config, output_format)
            elif provider == "coqui":
                return await self._synthesize_coqui(text, voice_config, output_format)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Provider {provider} synthesis failed: {str(e)}")
            raise
    
    async def _synthesize_edge_tts(
        self,
        text: str,
        voice_config: Dict[str, Any],
        output_format: AudioFormat
    ) -> Dict[str, Any]:
        """Synthesize using Edge TTS"""
        
        try:
            # Create output file path
            output_file = f"cache/voice/edge_tts_{int(time.time())}.{output_format.value}"
            
            # Configure voice
            voice = voice_config['edge_tts']
            rate = voice_config.get('rate', '+0%')
            volume = voice_config.get('volume', '+0%')
            
            # Generate speech
            communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
            await communicate.save(output_file)
            
            # Get duration
            duration = self._get_audio_duration(output_file)
            
            return {
                'success': True,
                'audio_path': output_file,
                'duration': duration,
                'provider': 'edge_tts'
            }
            
        except Exception as e:
            raise Exception(f"Edge TTS synthesis failed: {str(e)}")
    
    async def _synthesize_azure(
        self,
        text: str,
        voice_config: Dict[str, Any],
        output_format: AudioFormat
    ) -> Dict[str, Any]:
        """Synthesize using Azure Speech"""
        
        try:
            # Create output file path
            output_file = f"cache/voice/azure_{int(time.time())}.{output_format.value}"
            
            # Configure speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.api_keys.azure_speech_key,
                region=settings.api_keys.azure_speech_region
            )
            
            # Set voice
            voice = voice_config['azure']
            speech_config.speech_synthesis_voice_name = voice
            
            # Set output format
            if output_format == AudioFormat.MP3:
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
                )
            elif output_format == AudioFormat.WAV:
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
                )
            
            # Create audio config
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=audio_config
            )
            
            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                duration = self._get_audio_duration(output_file)
                return {
                    'success': True,
                    'audio_path': output_file,
                    'duration': duration,
                    'provider': 'azure'
                }
            else:
                raise Exception(f"Azure synthesis failed: {result.reason}")
                
        except Exception as e:
            raise Exception(f"Azure synthesis failed: {str(e)}")
    
    async def _synthesize_elevenlabs(
        self,
        text: str,
        voice_config: Dict[str, Any],
        output_format: AudioFormat,
        quality: str
    ) -> Dict[str, Any]:
        """Synthesize using ElevenLabs"""
        
        try:
            # Create output file path
            output_file = f"cache/voice/elevenlabs_{int(time.time())}.{output_format.value}"
            
            # Get voice ID
            voice_id = voice_config['elevenlabs']
            
            # Configure generation parameters
            model = "eleven_multilingual_v2" if quality == "ultra" else "eleven_monolingual_v1"
            
            # Generate audio
            audio = generate(
                text=text,
                voice=voice_id,
                model=model,
                output_format=output_format.value
            )
            
            # Save audio
            save(audio, output_file)
            
            # Get duration
            duration = self._get_audio_duration(output_file)
            
            return {
                'success': True,
                'audio_path': output_file,
                'duration': duration,
                'provider': 'elevenlabs'
            }
            
        except Exception as e:
            raise Exception(f"ElevenLabs synthesis failed: {str(e)}")
    
    async def _synthesize_google_tts(
        self,
        text: str,
        voice_config: Dict[str, Any],
        output_format: AudioFormat
    ) -> Dict[str, Any]:
        """Synthesize using Google Text-to-Speech"""
        
        try:
            # Create output file path
            output_file = f"cache/voice/google_tts_{int(time.time())}.{output_format.value}"
            
            # Google TTS API call
            url = "https://texttospeech.googleapis.com/v1/text:synthesize"
            headers = {
                "Authorization": f"Bearer {settings.api_keys.google_tts_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": {"text": text},
                "voice": {
                    "languageCode": "en-US",
                    "name": "en-US-Standard-A",
                    "ssmlGender": "FEMALE"
                },
                "audioConfig": {
                    "audioEncoding": "MP3" if output_format == AudioFormat.MP3 else "LINEAR16",
                    "speakingRate": 1.0,
                    "pitch": 0.0,
                    "volumeGainDb": 0.0
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                audio_content = result['audioContent']
                
                # Save audio
                import base64
                audio_data = base64.b64decode(audio_content)
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                
                duration = self._get_audio_duration(output_file)
                
                return {
                    'success': True,
                    'audio_path': output_file,
                    'duration': duration,
                    'provider': 'google_tts'
                }
            else:
                raise Exception(f"Google TTS API error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Google TTS synthesis failed: {str(e)}")
    
    async def _synthesize_coqui(
        self,
        text: str,
        voice_config: Dict[str, Any],
        output_format: AudioFormat
    ) -> Dict[str, Any]:
        """Synthesize using Coqui TTS (local)"""
        
        try:
            from TTS.api import TTS
            
            # Create output file path
            output_file = f"cache/voice/coqui_{int(time.time())}.{output_format.value}"
            
            # Initialize TTS
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            
            # Generate speech
            tts.tts_to_file(text=text, file_path=output_file)
            
            # Get duration
            duration = self._get_audio_duration(output_file)
            
            return {
                'success': True,
                'audio_path': output_file,
                'duration': duration,
                'provider': 'coqui'
            }
            
        except ImportError:
            raise Exception("Coqui TTS not available")
        except Exception as e:
            raise Exception(f"Coqui TTS synthesis failed: {str(e)}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            if audio_path.endswith('.wav'):
                with wave.open(audio_path, 'rb') as audio_file:
                    frames = audio_file.getnframes()
                    rate = audio_file.getframerate()
                    duration = frames / float(rate)
                    return duration
            else:
                # Use pydub for other formats
                audio = AudioSegment.from_file(audio_path)
                return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            self.logger.warning(f"Could not determine audio duration: {str(e)}")
            return 0.0
    
    async def _enhance_audio_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance audio quality for ultra quality setting"""
        
        try:
            audio_path = result['audio_path']
            enhanced_path = audio_path.replace('.', '_enhanced.')
            
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Apply enhancements
            # 1. Normalize volume
            audio = audio.normalize()
            
            # 2. Apply compression for better dynamics
            audio = audio.compress_dynamic_range()
            
            # 3. Enhance clarity with EQ
            # Boost frequencies around 2-4kHz for clarity
            audio = audio.high_pass_filter(80)  # Remove low rumble
            audio = audio.low_pass_filter(8000)  # Remove high noise
            
            # 4. Apply subtle reverb for depth
            # This is a simplified reverb effect
            audio = audio.fade_in(50).fade_out(50)
            
            # 5. Optimize for target format
            if enhanced_path.endswith('.mp3'):
                audio.export(enhanced_path, format='mp3', bitrate='192k')
            else:
                audio.export(enhanced_path, format=enhanced_path.split('.')[-1])
            
            # Update result
            result['audio_path'] = enhanced_path
            result['enhanced'] = True
            
            # Clean up original file
            try:
                os.remove(audio_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Audio enhancement failed: {str(e)}")
            return result
    
    @time_operation("voice_batch_synthesis")
    async def synthesize_batch(
        self,
        texts: List[str],
        voice_preset: VoicePreset = VoicePreset.PROFESSIONAL,
        provider: str = "auto",
        output_format: AudioFormat = AudioFormat.MP3,
        quality: str = "high"
    ) -> Dict[str, Any]:
        """Synthesize multiple text segments in batch"""
        
        try:
            results = []
            total_duration = 0.0
            
            # Process texts sequentially to avoid overwhelming providers
            for i, text in enumerate(texts):
                self.logger.info(f"Processing text segment {i+1}/{len(texts)}")
                
                result = await self.synthesize_speech(
                    text, voice_preset, provider, output_format, quality
                )
                
                if result['success']:
                    results.append(result)
                    total_duration += result['duration']
                else:
                    self.logger.error(f"Failed to synthesize segment {i+1}: {result['error']}")
                    results.append({
                        'success': False,
                        'error': result['error'],
                        'segment_index': i
                    })
            
            # Calculate success rate
            successful = sum(1 for r in results if r['success'])
            success_rate = (successful / len(results)) * 100 if results else 0
            
            return {
                'success': success_rate > 0,
                'results': results,
                'total_segments': len(texts),
                'successful_segments': successful,
                'success_rate': success_rate,
                'total_duration': total_duration,
                'provider': provider,
                'voice_preset': voice_preset.value
            }
            
        except Exception as e:
            self.logger.error(f"Batch synthesis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_available_voices(self) -> Dict[str, List[str]]:
        """Get available voices for each provider"""
        voices = {}
        
        if self.edge_available:
            voices['edge_tts'] = [
                'en-US-DavisNeural', 'en-US-JennyNeural', 'en-US-AriaNeural',
                'en-US-SaraNeural', 'en-US-GuyNeural', 'en-US-TonyNeural'
            ]
        
        if self.azure_available:
            voices['azure'] = [
                'en-US-DavisNeural', 'en-US-JennyNeural', 'en-US-AriaNeural',
                'en-US-SaraNeural', 'en-US-GuyNeural', 'en-US-TonyNeural'
            ]
        
        if self.elevenlabs_available:
            voices['elevenlabs'] = [
                'pNInz6obpgDQGcFmaJgB', 'EXAVITQu4vr4xnSDxMaL',
                '21m00Tcm4TlvDq8ikWAM', 'AZnzlk1XvdvUeBnXmlld'
            ]
        
        return voices
    
    def get_voice_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available voice presets"""
        return {
            preset.value: {
                'name': preset.value.replace('_', ' ').title(),
                'description': f"{preset.value.replace('_', ' ').title()} voice preset",
                'providers': list(self.voice_presets[preset].keys())[:-3],  # Exclude style, rate, volume
                'style': self.voice_presets[preset]['style'],
                'rate': self.voice_presets[preset]['rate'],
                'volume': self.voice_presets[preset]['volume']
            }
            for preset in self.voice_presets.keys()
        }
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all voice providers"""
        status = {}
        
        providers = {
            'edge_tts': self.edge_available,
            'azure': self.azure_available,
            'elevenlabs': self.elevenlabs_available,
            'google_tts': self.google_tts_available,
            'coqui': self.coqui_available
        }
        
        for provider, available in providers.items():
            status[provider] = {
                'available': available,
                'status': 'active' if available else 'unavailable',
                'quality_levels': self._get_provider_quality_levels(provider),
                'last_check': datetime.now().isoformat()
            }
        
        return status
    
    def _get_provider_quality_levels(self, provider: str) -> List[str]:
        """Get supported quality levels for provider"""
        quality_levels = {
            'edge_tts': ['low', 'medium', 'high'],
            'azure': ['low', 'medium', 'high', 'ultra'],
            'elevenlabs': ['medium', 'high', 'ultra'],
            'google_tts': ['low', 'medium', 'high'],
            'coqui': ['low', 'medium']
        }
        
        return quality_levels.get(provider, ['medium'])
