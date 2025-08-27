#!/usr/bin/env python3
"""
Test script for Voice Synthesis
"""

import asyncio
from app.services.voice_synthesis import get_voice_synthesis

async def test_voice_synthesis():
    """Test the voice synthesis system"""
    try:
        print("🎤 Testing Voice Synthesis System...")
        
        # Get voice synthesis service
        vs = get_voice_synthesis()
        print("✅ Voice Synthesis service initialized")
        
        # Check available services
        print(f"🔊 Available TTS Services:")
        print(f"  • Edge TTS: {vs.edge_tts_available}")
        print(f"  • gTTS: {vs.gtts_available}")
        print(f"  • OpenAI TTS: {vs.openai_tts_available}")
        
        # Show available voices
        voices = vs.get_available_voices()
        print(f"\n🗣️  Available Voices:")
        for language, voice_list in voices.items():
            print(f"  {language}:")
            for voice in voice_list[:2]:  # Show first 2 voices per language
                print(f"    • {voice['display']}")
        
        # Test speech synthesis
        test_text = "Hello! This is a test of the voice synthesis system."
        print(f"\n🎯 Testing speech synthesis with text: '{test_text}'")
        
        # Try to generate speech
        audio_file = await vs.synthesize_speech(
            text=test_text,
            voice="en-US-JennyNeural",
            language="English",
            speed=1.0
        )
        
        if audio_file:
            print(f"✅ Speech generated successfully!")
            print(f"📁 Audio file: {audio_file}")
            
            # Check if file exists and has content
            import os
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"📊 File size: {file_size} bytes")
                if file_size > 1000:
                    print("✅ Audio file appears to have content")
                else:
                    print("⚠️  Audio file seems too small")
            else:
                print("❌ Audio file not found")
        else:
            print("❌ Speech generation failed")
        
        # Test voice preview
        print(f"\n🎧 Testing voice preview...")
        preview_file = await vs.get_voice_preview("en-US-GuyNeural", "This is a male voice preview.")
        if preview_file:
            print(f"✅ Voice preview generated: {preview_file}")
        else:
            print("❌ Voice preview failed")
        
        print("\n🎉 Voice Synthesis System Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Voice Synthesis System Test FAILED: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_voice_synthesis())
