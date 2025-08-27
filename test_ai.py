#!/usr/bin/env python3
"""
Test script for AI Content Generation
"""

from app.services.ai_content_generator import get_ai_generator

def test_ai_generation():
    """Test AI content generation"""
    try:
        print("🤖 Testing AI Content Generation...")
        
        # Get AI generator
        ai_gen = get_ai_generator()
        print("✅ AI Generator initialized")
        
        # Generate a test script
        script = ai_gen.generate_video_script(
            topic="Digital Marketing Strategies",
            style="Professional",
            duration=15,
            target_audience="Business",
            language="English"
        )
        
        print("✅ AI Script generated successfully!")
        print(f"📝 Script Title: {script.get('title', 'N/A')}")
        print(f"📊 Number of Sections: {len(script.get('sections', []))}")
        print(f"⏱️ Total Duration: {script.get('total_duration', 'N/A')} seconds")
        print(f"🎨 Style Notes: {script.get('style_notes', 'N/A')}")
        
        # Show sections
        print("\n📋 Script Sections:")
        for i, section in enumerate(script.get('sections', []), 1):
            print(f"  {i}. {section.get('title', 'N/A')} ({section.get('duration', 'N/A')}s)")
            print(f"     {section.get('content', 'N/A')[:100]}...")
        
        print("\n🎉 AI Content Generation Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ AI Content Generation Test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_ai_generation()
