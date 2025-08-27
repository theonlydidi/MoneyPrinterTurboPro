"""
Professional Video Templates for MoneyPrinterTurboPro
Industry-specific templates with consistent branding and styles
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger


class VideoTemplate:
    """Base video template class"""
    
    def __init__(self, name: str, category: str, description: str):
        self.name = name
        self.category = category
        self.description = description
        self.settings = {}
        self.visual_elements = []
        self.transitions = []
        self.color_scheme = {}
        self.typography = {}
    
    def get_settings(self) -> Dict[str, Any]:
        """Get template settings"""
        return self.settings
    
    def get_visual_elements(self) -> List[str]:
        """Get visual elements for this template"""
        return self.visual_elements
    
    def get_transitions(self) -> List[str]:
        """Get transition effects for this template"""
        return self.transitions


class BusinessTemplate(VideoTemplate):
    """Professional business video template"""
    
    def __init__(self):
        super().__init__(
            name="Business Professional",
            category="Business",
            description="Clean, corporate-style videos for business presentations and marketing"
        )
        
        self.settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "duration": 15,
            "quality": "high"
        }
        
        self.visual_elements = [
            "Corporate logo placement",
            "Professional color scheme",
            "Clean typography",
            "Data visualizations",
            "Professional transitions",
            "Branded lower thirds",
            "Progress indicators"
        ]
        
        self.transitions = ["fade", "slide", "dissolve"]
        
        self.color_scheme = {
            "primary": "#2C3E50",      # Dark blue
            "secondary": "#3498DB",    # Light blue
            "accent": "#E74C3C",       # Red
            "background": "#ECF0F1",   # Light gray
            "text": "#2C3E50"          # Dark blue
        }
        
        self.typography = {
            "title_font": "Arial Bold",
            "body_font": "Arial",
            "title_size": 48,
            "body_size": 24
        }


class EducationalTemplate(VideoTemplate):
    """Educational video template"""
    
    def __init__(self):
        super().__init__(
            name="Educational",
            category="Education",
            description="Clear, engaging videos for learning and tutorials"
        )
        
        self.settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "duration": 20,
            "quality": "high"
        }
        
        self.visual_elements = [
            "Step-by-step guides",
            "Educational diagrams",
            "Progress bars",
            "Highlighted key points",
            "Clear text overlays",
            "Visual examples",
            "Learning objectives"
        ]
        
        self.transitions = ["fade", "zoom", "slide"]
        
        self.color_scheme = {
            "primary": "#27AE60",      # Green
            "secondary": "#2ECC71",    # Light green
            "accent": "#F39C12",       # Orange
            "background": "#FFFFFF",   # White
            "text": "#2C3E50"          # Dark blue
        }
        
        self.typography = {
            "title_font": "Arial Bold",
            "body_font": "Arial",
            "title_size": 42,
            "body_size": 28
        }


class CreativeTemplate(VideoTemplate):
    """Creative and artistic video template"""
    
    def __init__(self):
        super().__init__(
            name="Creative",
            category="Creative",
            description="Vibrant, artistic videos with dynamic effects and animations"
        )
        
        self.settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "duration": 15,
            "quality": "high"
        }
        
        self.visual_elements = [
            "Dynamic animations",
            "Colorful graphics",
            "Creative transitions",
            "Artistic effects",
            "Playful elements",
            "Vibrant backgrounds",
            "Animated text"
        ]
        
        self.transitions = ["zoom", "rotate", "morph", "wipe"]
        
        self.color_scheme = {
            "primary": "#9B59B6",      # Purple
            "secondary": "#E74C3C",    # Red
            "accent": "#F1C40F",       # Yellow
            "background": "#2C3E50",   # Dark blue
            "text": "#FFFFFF"          # White
        }
        
        self.typography = {
            "title_font": "Arial Black",
            "body_font": "Arial",
            "title_size": 52,
            "body_size": 26
        }


class MarketingTemplate(VideoTemplate):
    """Marketing and promotional video template"""
    
    def __init__(self):
        super().__init__(
            name="Marketing",
            category="Marketing",
            description="Engaging videos for product promotion and marketing campaigns"
        )
        
        self.settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "duration": 30,
            "quality": "high"
        }
        
        self.visual_elements = [
            "Product showcases",
            "Call-to-action buttons",
            "Social proof elements",
            "Brand messaging",
            "Engaging visuals",
            "Conversion elements",
            "Contact information"
        ]
        
        self.transitions = ["fade", "slide", "zoom", "dissolve"]
        
        self.color_scheme = {
            "primary": "#E74C3C",      # Red
            "secondary": "#F39C12",    # Orange
            "accent": "#3498DB",       # Blue
            "background": "#FFFFFF",   # White
            "text": "#2C3E50"          # Dark blue
        }
        
        self.typography = {
            "title_font": "Arial Bold",
            "body_font": "Arial",
            "title_size": 46,
            "body_size": 24
        }


class SocialMediaTemplate(VideoTemplate):
    """Social media optimized video template"""
    
    def __init__(self):
        super().__init__(
            name="Social Media",
            category="Social Media",
            description="Optimized videos for social media platforms with engaging content"
        )
        
        self.settings = {
            "resolution": "1080x1080",  # Square for social media
            "fps": 30,
            "duration": 15,
            "quality": "medium"
        }
        
        self.visual_elements = [
            "Eye-catching thumbnails",
            "Social media branding",
            "Engaging captions",
            "Trending elements",
            "Shareable content",
            "Platform optimization",
            "Viral potential"
        ]
        
        self.transitions = ["fade", "slide", "zoom"]
        
        self.color_scheme = {
            "primary": "#1ABC9C",      # Teal
            "secondary": "#F39C12",    # Orange
            "accent": "#E74C3C",       # Red
            "background": "#FFFFFF",   # White
            "text": "#2C3E50"          # Dark blue
        }
        
        self.typography = {
            "title_font": "Arial Bold",
            "body_font": "Arial",
            "title_size": 44,
            "body_size": 22
        }


class CorporateTemplate(VideoTemplate):
    """Corporate and enterprise video template"""
    
    def __init__(self):
        super().__init__(
            name="Corporate",
            category="Corporate",
            description="Formal, professional videos for corporate communications and training"
        )
        
        self.settings = {
            "resolution": "1920x1080",
            "fps": 30,
            "duration": 25,
            "quality": "high"
        }
        
        self.visual_elements = [
            "Corporate branding",
            "Professional layout",
            "Formal typography",
            "Business graphics",
            "Corporate colors",
            "Professional transitions",
            "Brand consistency"
        ]
        
        self.transitions = ["fade", "slide", "dissolve"]
        
        self.color_scheme = {
            "primary": "#34495E",      # Dark gray
            "secondary": "#7F8C8D",    # Medium gray
            "accent": "#3498DB",       # Blue
            "background": "#FFFFFF",   # White
            "text": "#2C3E50"          # Dark blue
        }
        
        self.typography = {
            "title_font": "Times New Roman Bold",
            "body_font": "Times New Roman",
            "title_size": 44,
            "body_size": 24
        }


class TemplateManager:
    """Manages video templates and provides template selection"""
    
    def __init__(self):
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all available templates"""
        self.templates = {
            "business": BusinessTemplate(),
            "educational": EducationalTemplate(),
            "creative": CreativeTemplate(),
            "marketing": MarketingTemplate(),
            "social_media": SocialMediaTemplate(),
            "corporate": CorporateTemplate()
        }
        
        logger.info(f"✅ Loaded {len(self.templates)} video templates")
    
    def get_template(self, template_name: str) -> Optional[VideoTemplate]:
        """Get a specific template by name"""
        return self.templates.get(template_name.lower())
    
    def get_all_templates(self) -> Dict[str, VideoTemplate]:
        """Get all available templates"""
        return self.templates
    
    def get_templates_by_category(self, category: str) -> List[VideoTemplate]:
        """Get templates filtered by category"""
        return [t for t in self.templates.values() if t.category.lower() == category.lower()]
    
    def get_template_names(self) -> List[str]:
        """Get list of all template names"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get detailed information about a template"""
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            "name": template.name,
            "category": template.category,
            "description": template.description,
            "settings": template.settings,
            "visual_elements": template.visual_elements,
            "transitions": template.transitions,
            "color_scheme": template.color_scheme,
            "typography": template.typography
        }
    
    def create_custom_template(
        self, 
        name: str, 
        category: str, 
        description: str,
        settings: Dict[str, Any],
        visual_elements: List[str],
        transitions: List[str],
        color_scheme: Dict[str, str],
        typography: Dict[str, Any]
    ) -> VideoTemplate:
        """Create a custom template"""
        template = VideoTemplate(name, category, description)
        template.settings = settings
        template.visual_elements = visual_elements
        template.transitions = transitions
        template.color_scheme = color_scheme
        template.typography = typography
        
        # Add to templates
        self.templates[name.lower()] = template
        
        logger.info(f"✅ Custom template '{name}' created successfully")
        return template
    
    def export_template(self, template_name: str, file_path: str) -> bool:
        """Export template to JSON file"""
        try:
            template = self.get_template(template_name)
            if not template:
                return False
            
            template_data = self.get_template_info(template_name)
            
            with open(file_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            logger.info(f"✅ Template '{template_name}' exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export template: {e}")
            return False
    
    def import_template(self, file_path: str) -> bool:
        """Import template from JSON file"""
        try:
            with open(file_path, 'r') as f:
                template_data = json.load(f)
            
            template = VideoTemplate(
                template_data["name"],
                template_data["category"],
                template_data["description"]
            )
            
            template.settings = template_data.get("settings", {})
            template.visual_elements = template_data.get("visual_elements", [])
            template.transitions = template_data.get("transitions", [])
            template.color_scheme = template_data.get("color_scheme", {})
            template.typography = template_data.get("typography", {})
            
            self.templates[template.name.lower()] = template
            
            logger.info(f"✅ Template '{template.name}' imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to import template: {e}")
            return False


# Global template manager instance
template_manager = TemplateManager()


def get_template_manager() -> TemplateManager:
    """Get the global template manager instance"""
    return template_manager


def get_template(template_name: str) -> Optional[VideoTemplate]:
    """Get a specific template by name"""
    return template_manager.get_template(template_name)


def get_all_templates() -> Dict[str, VideoTemplate]:
    """Get all available templates"""
    return template_manager.get_all_templates()
