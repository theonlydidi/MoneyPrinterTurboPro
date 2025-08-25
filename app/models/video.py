"""
Video models for MoneyPrinterTurboPro
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
import uuid


class VideoStatus(str, Enum):
    """Video generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoQuality(str, Enum):
    """Video quality presets"""
    LOW = "low"          # 480p, 30fps
    MEDIUM = "medium"    # 720p, 30fps
    HIGH = "high"        # 1080p, 30fps
    ULTRA = "ultra"      # 4K, 60fps


class VideoStyle(str, Enum):
    """Video style presets"""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    MINIMALIST = "minimalist"
    DYNAMIC = "dynamic"
    CORPORATE = "corporate"
    SOCIAL_MEDIA = "social_media"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"


class AudioFormat(str, Enum):
    """Audio format options"""
    MP3 = "mp3"
    WAV = "wav"
    AAC = "aac"
    FLAC = "flac"


class VideoFormat(str, Enum):
    """Video format options"""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WEBM = "webm"


class TransitionType(str, Enum):
    """Video transition types"""
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    ROTATE = "rotate"
    NONE = "none"


class VoicePreset(str, Enum):
    """Voice synthesis presets"""
    MALE_1 = "male_1"
    MALE_2 = "male_2"
    FEMALE_1 = "female_1"
    FEMALE_2 = "female_2"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"
    PROFESSIONAL = "professional"


class VideoRequest(BaseModel):
    """Video generation request"""
    
    # Basic information
    title: str = Field(..., min_length=1, max_length=200, description="Video title")
    description: str = Field(..., min_length=10, max_length=2000, description="Video description or script")
    duration: int = Field(..., ge=5, le=600, description="Target duration in seconds")
    
    # Style and quality
    style: VideoStyle = Field(default=VideoStyle.PROFESSIONAL, description="Video style preset")
    quality: VideoQuality = Field(default=VideoQuality.HIGH, description="Video quality preset")
    
    # Audio settings
    voice_preset: VoicePreset = Field(default=VoicePreset.PROFESSIONAL, description="Voice synthesis preset")
    background_music: bool = Field(default=True, description="Include background music")
    music_intensity: str = Field(default="medium", regex="^(low|medium|high)$", description="Music intensity")
    
    # Video settings
    aspect_ratio: str = Field(default="16:9", regex="^(16:9|9:16|4:3|1:1)$", description="Video aspect ratio")
    transitions: TransitionType = Field(default=TransitionType.FADE, description="Transition type between scenes")
    
    # AI settings
    ai_model: str = Field(default="gpt-4", description="AI model for script generation")
    language: str = Field(default="en", min_length=2, max_length=5, description="Content language")
    
    # Advanced options
    custom_prompts: Optional[List[str]] = Field(default=None, description="Custom AI prompts")
    exclude_keywords: Optional[List[str]] = Field(default=None, description="Keywords to exclude")
    include_subtitles: bool = Field(default=True, description="Generate subtitles")
    
    # Metadata
    tags: Optional[List[str]] = Field(default=None, description="Video tags")
    category: Optional[str] = Field(default=None, description="Video category")
    
    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v.strip()
    
    @validator('custom_prompts')
    def validate_custom_prompts(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 custom prompts allowed')
            for prompt in v:
                if len(prompt.strip()) < 5:
                    raise ValueError('Each custom prompt must be at least 5 characters')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to AI Video Generation",
                "description": "A comprehensive guide to creating professional videos using artificial intelligence. This video will cover the basics of AI-powered video creation, including script generation, voice synthesis, and automated editing.",
                "duration": 120,
                "style": "educational",
                "quality": "high",
                "voice_preset": "professional",
                "background_music": True,
                "music_intensity": "medium",
                "aspect_ratio": "16:9",
                "transitions": "fade",
                "ai_model": "gpt-4",
                "language": "en",
                "include_subtitles": True,
                "tags": ["AI", "Video", "Education", "Technology"],
                "category": "Technology"
            }
        }


class VideoResponse(BaseModel):
    """Video generation response"""
    
    video_id: str = Field(..., description="Unique video identifier")
    status: VideoStatus = Field(..., description="Current video status")
    title: str = Field(..., description="Video title")
    
    # Progress information
    progress: float = Field(..., ge=0.0, le=100.0, description="Generation progress percentage")
    current_step: str = Field(..., description="Current processing step")
    estimated_time: Optional[int] = Field(None, ge=0, description="Estimated time remaining in seconds")
    
    # Output information
    output_path: Optional[str] = Field(None, description="Path to generated video file")
    thumbnail_path: Optional[str] = Field(None, description="Path to video thumbnail")
    duration: Optional[float] = Field(None, ge=0, description="Final video duration in seconds")
    file_size: Optional[int] = Field(None, ge=0, description="Video file size in bytes")
    
    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    
    # Generation details
    generation_time: Optional[float] = Field(None, ge=0, description="Total generation time in seconds")
    quality_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="AI-generated quality score")
    
    class Config:
        schema_extra = {
            "example": {
                "video_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "title": "Introduction to AI Video Generation",
                "progress": 65.5,
                "current_step": "Applying video effects",
                "estimated_time": 45,
                "output_path": "/videos/output_550e8400.mp4",
                "thumbnail_path": "/thumbnails/thumb_550e8400.jpg",
                "duration": 120.5,
                "file_size": 15728640,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:35:00Z",
                "generation_time": 300.0,
                "quality_score": 8.7
            }
        }


class VideoTemplate(BaseModel):
    """Video template for quick generation"""
    
    template_id: str = Field(..., description="Template identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str = Field(..., min_length=10, max_length=500, description="Template description")
    
    # Template settings
    style: VideoStyle = Field(..., description="Default video style")
    quality: VideoQuality = Field(..., description="Default video quality")
    voice_preset: VoicePreset = Field(..., description="Default voice preset")
    aspect_ratio: str = Field(..., description="Default aspect ratio")
    transitions: TransitionType = Field(..., description="Default transition type")
    
    # Template prompts
    system_prompt: str = Field(..., description="System prompt for AI generation")
    example_prompts: List[str] = Field(..., description="Example user prompts")
    
    # Metadata
    category: str = Field(..., description="Template category")
    tags: List[str] = Field(..., description="Template tags")
    popularity: int = Field(default=0, ge=0, description="Template popularity score")
    
    # Usage statistics
    usage_count: int = Field(default=0, ge=0, description="Number of times template used")
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average user rating")
    
    created_at: datetime = Field(..., description="Template creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "template_id": "template_001",
                "name": "Product Demo",
                "description": "Professional product demonstration video template",
                "style": "corporate",
                "quality": "high",
                "voice_preset": "professional",
                "aspect_ratio": "16:9",
                "transitions": "slide",
                "system_prompt": "Create a compelling product demonstration video that highlights key features and benefits.",
                "example_prompts": [
                    "Showcase our new smartphone features",
                    "Demonstrate the benefits of our software solution"
                ],
                "category": "Marketing",
                "tags": ["Product", "Demo", "Marketing", "Corporate"],
                "popularity": 85,
                "usage_count": 150,
                "average_rating": 4.6,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z"
            }
        }


class VideoBatchRequest(BaseModel):
    """Batch video generation request"""
    
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Batch identifier")
    videos: List[VideoRequest] = Field(..., min_items=1, max_items=50, description="List of video requests")
    
    # Batch settings
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$", description="Batch priority")
    parallel_processing: bool = Field(default=True, description="Process videos in parallel")
    max_concurrent: int = Field(default=3, ge=1, le=10, description="Maximum concurrent processing")
    
    # Notification settings
    notify_on_completion: bool = Field(default=True, description="Send notification when batch completes")
    notify_on_failure: bool = Field(default=True, description="Send notification on any failure")
    
    @validator('videos')
    def validate_videos(cls, v):
        if len(v) > 50:
            raise ValueError('Maximum 50 videos per batch')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "batch_id": "batch_001",
                "videos": [
                    {
                        "title": "Video 1",
                        "description": "First video description",
                        "duration": 60
                    },
                    {
                        "title": "Video 2", 
                        "description": "Second video description",
                        "duration": 90
                    }
                ],
                "priority": "normal",
                "parallel_processing": True,
                "max_concurrent": 3
            }
        }


class VideoAnalytics(BaseModel):
    """Video generation analytics"""
    
    video_id: str = Field(..., description="Video identifier")
    
    # Performance metrics
    generation_time: float = Field(..., ge=0, description="Total generation time in seconds")
    processing_steps: Dict[str, float] = Field(..., description="Time spent on each processing step")
    
    # Quality metrics
    quality_score: float = Field(..., ge=0.0, le=10.0, description="AI-generated quality score")
    user_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="User rating")
    
    # Resource usage
    cpu_usage: float = Field(..., ge=0.0, le=100.0, description="Average CPU usage percentage")
    memory_usage: int = Field(..., ge=0, description="Peak memory usage in MB")
    gpu_usage: Optional[float] = Field(None, ge=0.0, le=100.0, description="GPU usage if available")
    
    # File metrics
    input_size: int = Field(..., ge=0, description="Input data size in bytes")
    output_size: int = Field(..., ge=0, description="Output video size in bytes")
    compression_ratio: float = Field(..., ge=0, description="Compression ratio")
    
    # User interaction
    views: int = Field(default=0, ge=0, description="Number of views")
    downloads: int = Field(default=0, ge=0, description="Number of downloads")
    shares: int = Field(default=0, ge=0, description="Number of shares")
    
    created_at: datetime = Field(..., description="Analytics creation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "video_id": "550e8400-e29b-41d4-a716-446655440000",
                "generation_time": 300.5,
                "processing_steps": {
                    "script_generation": 45.2,
                    "voice_synthesis": 67.8,
                    "video_processing": 187.5
                },
                "quality_score": 8.7,
                "user_rating": 4.5,
                "cpu_usage": 75.3,
                "memory_usage": 2048,
                "gpu_usage": 89.2,
                "input_size": 1048576,
                "output_size": 15728640,
                "compression_ratio": 15.0,
                "views": 150,
                "downloads": 45,
                "shares": 12,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
