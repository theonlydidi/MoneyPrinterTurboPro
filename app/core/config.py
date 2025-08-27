"""
Configuration management for MoneyPrinterTurboPro
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseModel):
    """Application basic settings"""
    name: str = "MoneyPrinterTurboPro"
    version: str = "2.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    webui_port: int = 8501
    workers: int = 4
    reload: bool = False
    
    # Feature flags
    enable_api: bool = True
    enable_webui: bool = True
    enable_auth: bool = True
    enable_rate_limit: bool = True
    enable_websocket: bool = True
    enable_gpu: bool = True
    enable_cache: bool = True
    
    # Video sources
    video_sources: List[str] = ["pexels", "pixabay", "unsplash", "local"]
    hide_config: bool = False


class QualityPreset(BaseModel):
    """Video quality preset configuration"""
    width: int
    height: int
    bitrate: str
    fps: int


class StylePreset(BaseModel):
    """Video style preset configuration"""
    transitions: List[str]
    filters: List[str]
    color_scheme: str


class APISettings(BaseModel):
    """API configuration"""
    prefix: str = "/api/v1"
    enable_cors: bool = True
    cors_origins: List[str] = ["*"]
    enable_docs: bool = True


class SecuritySettings(BaseModel):
    """Security configuration"""
    jwt_secret: str = "your-super-secret-jwt-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    bcrypt_rounds: int = 12


class RateLimitSettings(BaseModel):
    """Rate limiting configuration"""
    max_requests_per_minute: int = 60
    max_videos_per_user: int = 100
    max_concurrent_tasks: int = 4


class CacheSettings(BaseModel):
    """Cache configuration"""
    cache_dir: str = "./cache"
    cache_size_limit: str = "10GB"
    cache_ttl: int = 86400
    enable_memory_cache: bool = True
    memory_cache_size: str = "2GB"
    enable_disk_cache: bool = True
    disk_cache_size: str = "10GB"


class StorageSettings(BaseModel):
    """Storage configuration"""
    storage_type: str = "local"  # local, s3, azure, gcp
    storage_path: str = "./storage"
    temp_dir: str = "./temp"
    output_dir: str = "./output"
    cleanup_temp_files: bool = True
    temp_file_ttl: int = 3600


class VideoProcessingSettings(BaseModel):
    """Video processing configuration"""
    timeout: int = 1800
    max_duration: int = 600
    max_size: str = "2GB"
    enable_parallel: bool = True
    output_formats: List[str] = ["mp4", "mov", "webm", "avi"]
    default_quality: str = "1080p"
    default_fps: int = 30


class AISettings(BaseModel):
    """AI model configuration"""
    default_llm_provider: str = "openai"
    default_voice_provider: str = "azure"
    default_subtitle_provider: str = "whisper"


class MonitoringSettings(BaseModel):
    """Monitoring configuration"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    enable_health_check: bool = True
    health_check_interval: int = 30
    log_file: str = "./logs/moneyprinter_pro.log"
    log_max_size: str = "100MB"
    log_backup_count: int = 5


class PerformanceSettings(BaseModel):
    """Performance configuration"""
    gpu_memory_limit: str = "8GB"
    gpu_utilization: float = 0.8
    enable_mixed_precision: bool = True
    task_timeout: int = 1800
    memory_limit: str = "16GB"
    enable_video_compression: bool = True
    compression_quality: int = 85
    enable_audio_compression: bool = True
    audio_compression_quality: int = 128


class PluginSettings(BaseModel):
    """Plugin system configuration"""
    enable_plugins: bool = True
    plugin_directory: str = "./plugins"
    plugin_auto_load: bool = True
    available_plugins: List[str] = ["video_effects", "ai_models", "export_formats", "analytics"]


class DevelopmentSettings(BaseModel):
    """Development configuration"""
    debug: bool = False
    verbose_logging: bool = False
    dev_host: str = "127.0.0.1"
    dev_port: int = 8000
    dev_reload: bool = True
    test_mode: bool = False
    enable_swagger: bool = True
    enable_redoc: bool = True


class Settings(BaseSettings):
    """Main settings class"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields in config
    )
    
    # Core settings
    app: AppSettings = Field(default_factory=AppSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    video_processing: VideoProcessingSettings = Field(default_factory=VideoProcessingSettings)
    ai: AISettings = Field(default_factory=AISettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)
    development: DevelopmentSettings = Field(default_factory=DevelopmentSettings)
    
    # Quality and style presets
    quality_presets: Dict[str, QualityPreset] = Field(default_factory=dict)
    style_presets: Dict[str, StylePreset] = Field(default_factory=dict)
    
    # API Keys (loaded from environment or config)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    pexels_api_keys: List[str] = Field(default_factory=list)
    pixabay_api_keys: List[str] = Field(default_factory=list)
    unsplash_api_keys: List[str] = Field(default_factory=list)
    
    # Database and Redis
    database_url: str = "sqlite:///./moneyprinter_pro.db"
    redis_url: str = "redis://localhost:6379"
    
    def __init__(self, **kwargs):
        """Initialize settings with TOML file loading"""
        # Load TOML config first
        toml_config = self._load_toml_config()
        
        # Merge TOML config with kwargs
        merged_config = {**toml_config, **kwargs}
        
        # Call parent constructor
        super().__init__(**merged_config)
    
    def _load_toml_config(self) -> Dict[str, Any]:
        """Load configuration from TOML file"""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                # Fallback to basic config
                return {}
        
        config_path = Path("config.toml")
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, "rb") as f:
                toml_data = tomllib.load(f)
            
            # Convert TOML data to flat structure for Pydantic
            flat_config = self._flatten_toml(toml_data)
            return flat_config
            
        except Exception as e:
            print(f"Warning: Could not load TOML config: {e}")
            return {}
    
    def _flatten_toml(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested TOML structure for Pydantic compatibility"""
        flat = {}
        
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                flat.update(self._flatten_toml(value, f"{full_key}__"))
            else:
                # Convert value to string if it's a list or other complex type
                if isinstance(value, (list, dict)):
                    flat[full_key] = str(value)
                else:
                    flat[full_key] = value
        
        return flat
    
    @validator('app', pre=True)
    def load_app_settings(cls, v):
        """Load app settings from environment variables"""
        if isinstance(v, dict):
            return v
        
        return AppSettings(
            host=os.getenv("MONEYPRINTER_PRO_HOST", "0.0.0.0"),
            port=int(os.getenv("MONEYPRINTER_PRO_API_PORT", "8080")),
            webui_port=int(os.getenv("MONEYPRINTER_PRO_WEBUI_PORT", "8501")),
            workers=int(os.getenv("MONEYPRINTER_PRO_WORKERS", "4")),
            reload=os.getenv("MONEYPRINTER_PRO_RELOAD", "false").lower() == "true",
            log_level=os.getenv("MONEYPRINTER_PRO_LOG_LEVEL", "INFO"),
            enable_api=os.getenv("MONEYPRINTER_PRO_ENABLE_API", "true").lower() == "true",
            enable_webui=os.getenv("MONEYPRINTER_PRO_ENABLE_WEBUI", "true").lower() == "true",
            enable_auth=os.getenv("MONEYPRINTER_PRO_ENABLE_AUTH", "true").lower() == "true",
            enable_rate_limit=os.getenv("MONEYPRINTER_PRO_ENABLE_RATE_LIMIT", "true").lower() == "true",
            enable_websocket=os.getenv("MONEYPRINTER_PRO_ENABLE_WEBSOCKET", "true").lower() == "true",
            enable_gpu=os.getenv("MONEYPRINTER_PRO_ENABLE_GPU", "true").lower() == "true",
            enable_cache=os.getenv("MONEYPRINTER_PRO_ENABLE_CACHE", "true").lower() == "true",
        )
    
    @validator('quality_presets', pre=True)
    def load_quality_presets(cls, v):
        """Load quality presets"""
        if isinstance(v, dict):
            return v
        
        return {
            "4k": QualityPreset(width=3840, height=2160, bitrate="50M", fps=30),
            "2k": QualityPreset(width=2560, height=1440, bitrate="25M", fps=30),
            "1080p": QualityPreset(width=1920, height=1080, bitrate="15M", fps=30),
            "720p": QualityPreset(width=1280, height=720, bitrate="8M", fps=30),
            "480p": QualityPreset(width=854, height=480, bitrate="4M", fps=30),
        }
    
    @validator('style_presets', pre=True)
    def load_style_presets(cls, v):
        """Load style presets"""
        if isinstance(v, dict):
            return v
        
        return {
            "modern": StylePreset(
                transitions=["fade", "slide"],
                filters=["vintage"],
                color_scheme="cool"
            ),
            "business": StylePreset(
                transitions=["fade"],
                filters=["professional"],
                color_scheme="warm"
            ),
            "creative": StylePreset(
                transitions=["zoom", "rotate"],
                filters=["artistic"],
                color_scheme="vibrant"
            ),
            "minimal": StylePreset(
                transitions=["fade"],
                filters=["clean"],
                color_scheme="monochrome"
            ),
        }
    
    @validator('openai_api_key', pre=True)
    def load_openai_key(cls, v):
        """Load OpenAI API key from environment"""
        return v or os.getenv("OPENAI_API_KEY")
    
    @validator('anthropic_api_key', pre=True)
    def load_anthropic_key(cls, v):
        """Load Anthropic API key from environment"""
        return v or os.getenv("ANTHROPIC_API_KEY")
    
    @validator('gemini_api_key', pre=True)
    def load_gemini_key(cls, v):
        """Load Gemini API key from environment"""
        return v or os.getenv("GOOGLE_API_KEY")
    
    @validator('azure_api_key', pre=True)
    def load_azure_key(cls, v):
        """Load Azure API key from environment"""
        return v or os.getenv("AZURE_OPENAI_API_KEY")
    
    @validator('pexels_api_keys', pre=True)
    def load_pexels_keys(cls, v):
        """Load Pexels API keys from environment"""
        if v:
            return v
        keys = os.getenv("PEXELS_API_KEYS")
        if keys:
            return [key.strip() for key in keys.split(",")]
        return []
    
    @validator('pixabay_api_keys', pre=True)
    def load_pixabay_keys(cls, v):
        """Load Pixabay API keys from environment"""
        if v:
            return v
        keys = os.getenv("PIXABAY_API_KEYS")
        if keys:
            return [key.strip() for key in keys.split(",")]
        return []
    
    @validator('unsplash_api_keys', pre=True)
    def load_unsplash_keys(cls, v):
        """Load Unsplash API keys from environment"""
        if v:
            return v
        keys = os.getenv("UNSPLASH_API_KEYS")
        if keys:
            return [key.strip() for key in keys.split(",")]
        return []
    
    def get_quality_preset(self, quality: str) -> Optional[QualityPreset]:
        """Get quality preset by name"""
        return self.quality_presets.get(quality)
    
    def get_style_preset(self, style: str) -> Optional[StylePreset]:
        """Get style preset by name"""
        return self.style_presets.get(style)
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return os.getenv("MONEYPRINTER_PRO_ENV", "production") == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.is_development()


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance"""
    return settings


def reload_settings() -> None:
    """Reload settings from configuration file"""
    global settings
    settings = Settings()


# Environment-specific settings
def get_env_settings() -> Dict[str, Any]:
    """Get environment-specific settings"""
    env = os.getenv("MONEYPRINTER_PRO_ENV", "production")
    
    if env == "development":
        return {
            "debug": True,
            "log_level": "DEBUG",
            "reload": True,
            "workers": 1,
        }
    elif env == "testing":
        return {
            "debug": True,
            "log_level": "DEBUG",
            "test_mode": True,
        }
    else:  # production
        return {
            "debug": False,
            "log_level": "INFO",
            "reload": False,
            "workers": 4,
        }
