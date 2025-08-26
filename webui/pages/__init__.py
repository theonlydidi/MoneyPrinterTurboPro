# Pages Package
from .dashboard import render_dashboard
from .video_generator import render_video_generator
from .templates import render_templates
from .analytics import render_analytics
from .settings import render_settings

__all__ = [
    'render_dashboard',
    'render_video_generator', 
    'render_templates',
    'render_analytics',
    'render_settings'
]
