import toml
import os

def get_config():
    """Get configuration from config.toml or environment variables"""
    config = {
        "app_name": "MoneyPrinterTurboPro",
        "version": "2.0.0",
        "debug": False,
        "api_url": os.getenv("API_URL", "http://localhost:8000"),
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", "100")),
        "supported_formats": ["mp4", "avi", "mov", "mkv"],
        "default_quality": "1080p",
        "default_duration": 60
    }
    
    # Try to load from config.toml if it exists
    try:
        if os.path.exists("config.toml"):
            with open("config.toml", "r") as f:
                file_config = toml.load(f)
                config.update(file_config)
    except Exception as e:
        print(f"Warning: Could not load config.toml: {e}")
    
    return config
