"""
Voice Synthesis Service for MoneyPrinterTurboPro
Text-to-speech functionality for video narration
"""

import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("Edge TTS not available. Install with: pip install edge-tts")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available. Install with: pip install gtts")

try:
    import openai
    OPENAI_TTS_AVAILABLE = True
except ImportError:
    OPENAI_TTS_AVAILABLE = False
    logger.warning("OpenAI TTS not available. Install with: pip install openai")


class VoiceSynthesis:
    """Voice synthesis service for video narration"""
    
    def __init__(self):
        self.edge_tts_available = EDGE_TTS_AVAILABLE
        self.gtts_available = GTTS_AVAILABLE
        self.openai_tts_available = OPENAI_TTS_AVAILABLE
        
        # Available voices
        self.voices = self._get_available_voices()
        
        logger.info(f"✅ Voice Synthesis initialized: Edge TTS: {self.edge_tts_available}, gTTS: {self.gtts_available}, OpenAI: {self.openai_tts_available}")
    
    def _get_available_voices(self) -> Dict[str, List[Dict[str, str]]]:
        """Get available voices for different languages"""
        voices = {
            "English": [
                {"name": "en-US-JennyNeural", "display": "Jenny (Female, US)"},
                {"name": "en-US-GuyNeural", "display": "Guy (Male, US)"},
                {"name": "en-GB-SoniaNeural", "display": "Sonia (Female, UK)"},
                {"name": "en-GB-RyanNeural", "display": "Ryan (Male, UK)"},
                {"name": "en-AU-NatashaNeural", "display": "Natasha (Female, Australia)"}
            ],
            "Spanish": [
                {"name": "es-ES-ElviraNeural", "display": "Elvira (Female, Spain)"},
                {"name": "es-ES-AlvaroNeural", "display": "Alvaro (Male, Spain)"},
                {"name": "es-MX-JorgeNeural", "display": "Jorge (Male, Mexico)"}
            ],
            "French": [
                {"name": "fr-FR-DeniseNeural", "display": "Denise (Female, France)"},
                {"name": "fr-FR-HenriNeural", "display": "Henri (Male, France)"}
            ],
            "German": [
                {"name": "de-DE-KatjaNeural", "display": "Katja (Female, Germany)"},
                {"name": "de-DE-ConradNeural", "display": "Conrad (Male, Germany)"}
            ],
            "Chinese": [
                {"name": "zh-CN-XiaoxiaoNeural", "display": "Xiaoxiao (Female, China)"},
                {"name": "zh-CN-YunxiNeural", "display": "Yunxi (Male, China)"}
            ],
            "Japanese": [
                {"name": "ja-JP-NanamiNeural", "display": "Nanami (Female, Japan)"},
                {"name": "ja-JP-KeitaNeural", "display": "Keita (Male, Japan)"}
            ]
        }
        
        return voices
    
    def get_available_voices(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all available voices"""
        return self.voices
    
    def get_voices_for_language(self, language: str) -> List[Dict[str, str]]:
        """Get voices for a specific language"""
        return self.voices.get(language, [])
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice: str = "en-US-JennyNeural",
        language: str = "English",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Synthesize speech from text"""
        try:
            # Try Edge TTS first (best quality, free)
            if self.edge_tts_available:
                return await self._synthesize_with_edge_tts(text, voice, speed, output_path)
            
            # Fallback to gTTS
            elif self.gtts_available:
                return self._synthesize_with_gtts(text, language, output_path)
            
            # Fallback to OpenAI TTS
            elif self.openai_tts_available:
                return self._synthesize_with_openai(text, voice, output_path)
            
            else:
                logger.error("❌ No TTS service available")
                return None
                
        except Exception as e:
            logger.error(f"❌ Speech synthesis failed: {e}")
            return None
    
    async def _synthesize_with_edge_tts(
        self, 
        text: str, 
        voice: str, 
        speed: float, 
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Synthesize speech using Edge TTS"""
        try:
            if not output_path:
                # Create temporary file
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                output_path = temp_dir / f"speech_{hash(text) % 10000}.mp3"
            
            # Configure TTS
            communicate = edge_tts.Communicate(text, voice, rate=f"{int((speed - 1) * 100):+d}%")
            
            # Generate speech (await the async operation)
            await communicate.save(str(output_path))
            
            logger.info(f"✅ Edge TTS speech generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Edge TTS synthesis failed: {e}")
            return None
    
    def _synthesize_with_gtts(
        self, 
        text: str, 
        language: str, 
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Synthesize speech using gTTS"""
        try:
            if not output_path:
                # Create temporary file
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                output_path = temp_dir / f"speech_{hash(text) % 10000}.mp3"
            
            # Language mapping
            lang_map = {
                "English": "en",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
                "Chinese": "zh",
                "Japanese": "ja"
            }
            
            lang_code = lang_map.get(language, "en")
            
            # Generate speech
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(str(output_path))
            
            logger.info(f"✅ gTTS speech generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ gTTS synthesis failed: {e}")
            return None
    
    def _synthesize_with_openai(
        self, 
        text: str, 
        voice: str, 
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Synthesize speech using OpenAI TTS"""
        try:
            if not output_path:
                # Create temporary file
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                output_path = temp_dir / f"speech_{hash(text) % 10000}.mp3"
            
            # Voice mapping
            voice_map = {
                "en-US-JennyNeural": "alloy",
                "en-US-GuyNeural": "echo",
                "en-GB-SoniaNeural": "fable",
                "en-GB-RyanNeural": "onyx",
                "en-AU-NatashaNeural": "nova"
            }
            
            openai_voice = voice_map.get(voice, "alloy")
            
            # Generate speech
            response = openai.Audio.speech.create(
                model="tts-1",
                voice=openai_voice,
                input=text
            )
            
            # Save audio
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"✅ OpenAI TTS speech generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ OpenAI TTS synthesis failed: {e}")
            return None
    
    async def generate_video_narration(
        self, 
        script: Dict[str, Any], 
        voice: str = "en-US-JennyNeural",
        language: str = "English",
        speed: float = 1.0
    ) -> Dict[str, str]:
        """Generate narration for an entire video script"""
        try:
            narration_files = {}
            
            # Generate narration for hook
            if "hook" in script:
                hook_audio = await self.synthesize_speech(
                    script["hook"], voice, language, speed
                )
                if hook_audio:
                    narration_files["hook"] = hook_audio
            
            # Generate narration for sections
            if "sections" in script:
                for i, section in enumerate(script["sections"]):
                    section_content = section.get("content", "")
                    if section_content:
                        section_audio = await self.synthesize_speech(
                            section_content, voice, language, speed
                        )
                        if section_audio:
                            narration_files[f"section_{i}"] = section_audio
            
            # Generate narration for conclusion
            if "conclusion" in script:
                conclusion_audio = await self.synthesize_speech(
                    script["conclusion"], voice, language, speed
                )
                if conclusion_audio:
                    narration_files["conclusion"] = conclusion_audio
            
            logger.info(f"✅ Generated {len(narration_files)} narration files")
            return narration_files
            
        except Exception as e:
            logger.error(f"❌ Video narration generation failed: {e}")
            return {}
    
    async def get_voice_preview(self, voice: str, sample_text: str = "Hello, this is a voice preview.") -> Optional[str]:
        """Generate a voice preview for testing"""
        try:
            return await self.synthesize_speech(sample_text, voice, "English", 1.0)
        except Exception as e:
            logger.error(f"❌ Voice preview generation failed: {e}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        try:
            temp_dir = Path("temp")
            if temp_dir.exists():
                for file_path in temp_dir.glob("*.mp3"):
                    file_path.unlink()
                logger.info("✅ Temporary audio files cleaned up")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup temp files: {e}")


# Global voice synthesis instance
voice_synthesis = VoiceSynthesis()


def get_voice_synthesis() -> VoiceSynthesis:
    """Get the global voice synthesis instance"""
    return voice_synthesis


async def synthesize_speech(
    text: str, 
    voice: str = "en-US-JennyNeural",
    language: str = "English",
    speed: float = 1.0
) -> Optional[str]:
    """Quick function to synthesize speech"""
    vs = get_voice_synthesis()
    return await vs.synthesize_speech(text, voice, language, speed)
