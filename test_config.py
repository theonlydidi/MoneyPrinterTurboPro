#!/usr/bin/env python3
"""
Configuration Test Script for MoneyPrinterTurboPro
Tests API keys and configuration settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def test_configuration():
    """Test the configuration and API keys"""
    print("🔧 Testing MoneyPrinterTurboPro Configuration...")
    
    # Load environment variables
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✅ .env file loaded successfully")
    else:
        print("⚠️  .env file not found. Using env.template values")
        load_dotenv("env.template")
    
    print("\n📋 Configuration Status:")
    
    # Test OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        print(f"✅ OpenAI API Key: {openai_key[:20]}...")
    else:
        print("❌ OpenAI API Key: Not configured")
    
    # Test Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        print(f"✅ Anthropic API Key: {anthropic_key[:20]}...")
    else:
        print("❌ Anthropic API Key: Not configured")
    
    # Test Google
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key and google_key != "your_google_api_key_here":
        print(f"✅ Google API Key: {google_key[:20]}...")
    else:
        print("❌ Google API Key: Not configured")
    
    # Test Azure Speech
    azure_key = os.getenv("AZURE_SPEECH_KEY")
    if azure_key and azure_key != "your_azure_speech_key_here":
        print(f"✅ Azure Speech Key: {azure_key[:20]}...")
    else:
        print("⚠️  Azure Speech Key: Not configured (optional)")
    
    # Test ElevenLabs
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    if elevenlabs_key and elevenlabs_key != "your_elevenlabs_api_key_here":
        print(f"✅ ElevenLabs API Key: {elevenlabs_key[:20]}...")
    else:
        print("⚠️  ElevenLabs API Key: Not configured (optional)")
    
    # Test database
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"✅ Database URL: {db_url}")
    else:
        print("❌ Database URL: Not configured")
    
    # Test environment
    env = os.getenv("ENVIRONMENT", "development")
    debug = os.getenv("DEBUG", "false")
    print(f"✅ Environment: {env}")
    print(f"✅ Debug Mode: {debug}")
    
    print("\n🎯 API Key Status Summary:")
    
    required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    optional_keys = ["GOOGLE_API_KEY", "AZURE_SPEECH_KEY", "ELEVENLABS_API_KEY"]
    
    required_configured = 0
    for key in required_keys:
        if os.getenv(key) and os.getenv(key) != f"your_{key.lower()}_here":
            required_configured += 1
    
    optional_configured = 0
    for key in optional_keys:
        if os.getenv(key) and os.getenv(key) != f"your_{key.lower()}_here":
            optional_configured += 1
    
    print(f"  Required Keys: {required_configured}/{len(required_keys)} configured")
    print(f"  Optional Keys: {optional_configured}/{len(optional_keys)} configured")
    
    if required_configured >= 1:
        print("🎉 Configuration is ready for basic functionality!")
        if required_configured >= 2:
            print("🚀 Full AI functionality available!")
    else:
        print("❌ Configuration needs attention before use")
    
    return required_configured >= 1

if __name__ == "__main__":
    test_configuration()
