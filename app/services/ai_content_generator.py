"""
AI Content Generation Service for MoneyPrinterTurboPro
Uses OpenAI and other AI providers to generate real video content
"""

import os
import json
from typing import Dict, List, Optional, Any
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic not available. Install with: pip install anthropic")


class AIContentGenerator:
    """AI-powered content generation for videos"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI provider clients"""
        # OpenAI
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("⚠️  OpenAI API key not found in environment")
        
        # Anthropic
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                logger.info("✅ Anthropic client initialized")
            else:
                logger.warning("⚠️  Anthropic API key not found in environment")
    
    def generate_video_script(
        self, 
        topic: str, 
        style: str, 
        duration: int,
        target_audience: str = "general",
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate a complete video script using AI"""
        try:
            if self.openai_client:
                return self._generate_with_openai(topic, style, duration, target_audience, language)
            elif self.anthropic_client:
                return self._generate_with_anthropic(topic, style, duration, target_audience, language)
            else:
                return self._generate_fallback_script(topic, style, duration, target_audience, language)
        except Exception as e:
            logger.error(f"❌ AI script generation failed: {e}")
            return self._generate_fallback_script(topic, style, duration, target_audience, language)
    
    def _generate_with_openai(
        self, 
        topic: str, 
        style: str, 
        duration: int,
        target_audience: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate script using OpenAI GPT-4"""
        prompt = f"""
        Create a professional video script for a {duration}-second video about "{topic}".
        
        Style: {style}
        Target Audience: {target_audience}
        Language: {language}
        
        The script should include:
        1. Hook/Introduction (5-10 seconds)
        2. Main content with 3-5 key points
        3. Call-to-action conclusion
        
        Format the response as JSON with:
        {{
            "title": "Video title",
            "hook": "Opening hook text",
            "sections": [
                {{
                    "title": "Section title",
                    "content": "Section content",
                    "duration": "estimated seconds"
                }}
            ],
            "conclusion": "Call-to-action text",
            "total_duration": {duration},
            "style_notes": "Style-specific instructions",
            "visual_suggestions": ["visual element 1", "visual element 2"]
        }}
        
        Make it engaging, professional, and suitable for {style} style.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional video script writer specializing in engaging, educational content. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI response: {content[:200]}...")
            
            # Try to parse JSON, with fallback if it fails
            try:
                script_data = json.loads(content)
                logger.info(f"✅ OpenAI generated script for: {topic}")
                return script_data
            except json.JSONDecodeError as e:
                logger.warning(f"OpenAI response not valid JSON: {e}")
                logger.warning(f"Response content: {content}")
                raise
            
        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {e}")
            raise
    
    def _generate_with_anthropic(
        self, 
        topic: str, 
        style: str, 
        duration: int,
        target_audience: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate script using Anthropic Claude"""
        prompt = f"""
        Create a professional video script for a {duration}-second video about "{topic}".
        
        Style: {style}
        Target Audience: {target_audience}
        Language: {language}
        
        The script should include:
        1. Hook/Introduction (5-10 seconds)
        2. Main content with 3-5 key points
        3. Call-to-action conclusion
        
        Format the response as JSON with:
        {{
            "title": "Video title",
            "hook": "Opening hook text",
            "sections": [
                {{
                    "title": "Section title",
                    "content": "Section content",
                    "duration": "estimated seconds"
                }}
            ],
            "conclusion": "Call-to-action text",
            "total_duration": {duration},
            "style_notes": "Style-specific instructions",
            "visual_suggestions": ["visual element 1", "visual element 2"]
        }}
        
        Make it engaging, professional, and suitable for {style} style.
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            script_data = json.loads(content)
            logger.info(f"✅ Anthropic generated script for: {topic}")
            return script_data
            
        except Exception as e:
            logger.error(f"❌ Anthropic generation failed: {e}")
            raise
    
    def _generate_fallback_script(
        self, 
        topic: str, 
        style: str, 
        duration: int,
        target_audience: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate a fallback script when AI is not available"""
        logger.info("⚠️  Using fallback script generation (AI not available)")
        
        # Create a basic script structure
        sections = []
        section_duration = max(5, duration // 4)  # Divide into 4 sections
        
        if style == "Professional":
            sections = [
                {
                    "title": "Introduction",
                    "content": f"Welcome to this comprehensive guide on {topic}. Today, we'll explore the key aspects that make this topic essential for {target_audience}.",
                    "duration": section_duration
                },
                {
                    "title": "Key Concepts",
                    "content": f"Let's dive into the fundamental concepts of {topic}. Understanding these principles will give you a solid foundation.",
                    "duration": section_duration
                },
                {
                    "title": "Practical Applications",
                    "content": f"Now let's see how {topic} applies in real-world scenarios. These practical examples will help you implement what you've learned.",
                    "duration": section_duration
                },
                {
                    "title": "Best Practices",
                    "content": f"To ensure success with {topic}, follow these proven best practices. They'll help you avoid common pitfalls and achieve better results.",
                    "duration": section_duration
                }
            ]
        elif style == "Creative":
            sections = [
                {
                    "title": "The Magic Begins",
                    "content": f"Imagine a world where {topic} opens up endless possibilities. Let's embark on a creative journey together.",
                    "duration": section_duration
                },
                {
                    "title": "Breaking Boundaries",
                    "content": f"Creativity knows no limits when it comes to {topic}. Let's explore innovative approaches and think outside the box.",
                    "duration": section_duration
                },
                {
                    "title": "Inspiring Examples",
                    "content": f"Prepare to be amazed by these creative examples of {topic} in action. They'll spark your imagination and fuel your creativity.",
                    "duration": section_duration
                },
                {
                    "title": "Your Creative Journey",
                    "content": f"Now it's your turn to unleash your creativity with {topic}. The possibilities are endless, and your imagination is the only limit.",
                    "duration": section_duration
                }
            ]
        else:  # Educational style
            sections = [
                {
                    "title": "Learning Objectives",
                    "content": f"By the end of this video, you'll understand the core concepts of {topic} and be able to apply them effectively.",
                    "duration": section_duration
                },
                {
                    "title": "Core Concepts",
                    "content": f"Let's start with the essential concepts of {topic}. These building blocks will form the foundation of your knowledge.",
                    "duration": section_duration
                },
                {
                    "title": "Step-by-Step Process",
                    "content": f"Follow along as we break down {topic} into manageable steps. This systematic approach will make learning easier and more effective.",
                    "duration": section_duration
                },
                {
                    "title": "Practice and Review",
                    "content": f"Practice makes perfect! Let's review what we've learned about {topic} and ensure you're ready to apply your new knowledge.",
                    "duration": section_duration
                }
            ]
        
        return {
            "title": f"Complete Guide to {topic}",
            "hook": f"Ready to master {topic}? This comprehensive guide will take you from beginner to expert in just {duration} seconds.",
            "sections": sections,
            "conclusion": f"Congratulations! You've completed your journey into {topic}. Remember, the key to mastery is consistent practice and application.",
            "total_duration": duration,
            "style_notes": f"Style: {style} - Tailored for {target_audience}",
            "visual_suggestions": [
                "Progress indicators",
                "Key point highlights",
                "Visual examples",
                "Engaging graphics"
            ]
        }
    
    def generate_visual_suggestions(self, topic: str, style: str) -> List[str]:
        """Generate visual suggestions for video content"""
        suggestions = {
            "Professional": [
                "Clean, corporate-style graphics",
                "Data visualizations and charts",
                "Professional color scheme (blues, grays)",
                "Minimalist text overlays",
                "Smooth transitions between sections"
            ],
            "Creative": [
                "Vibrant, colorful animations",
                "Dynamic text effects",
                "Creative transitions (zoom, rotate, morph)",
                "Artistic graphics and illustrations",
                "Playful visual elements"
            ],
            "Educational": [
                "Clear, readable text",
                "Step-by-step visual guides",
                "Educational diagrams and charts",
                "Progress bars and indicators",
                "Highlighted key points"
            ]
        }
        
        return suggestions.get(style, suggestions["Professional"])
    
    def enhance_script_with_ai(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance an existing script with AI improvements"""
        try:
            if not self.openai_client and not self.anthropic_client:
                return script
            
            prompt = f"""
            Enhance this video script to make it more engaging and professional:
            
            {json.dumps(script, indent=2)}
            
            Improve:
            1. Hook to be more compelling
            2. Section content to be more engaging
            3. Conclusion to have stronger call-to-action
            4. Add visual suggestions
            
            Return the enhanced script in the same JSON format.
            """
            
            if self.openai_client:
                response = self.openai_client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a video script enhancement expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                enhanced_content = response.choices[0].message.content
                enhanced_script = json.loads(enhanced_content)
                logger.info("✅ Script enhanced with AI")
                return enhanced_script
                
        except Exception as e:
            logger.error(f"❌ Script enhancement failed: {e}")
            return script
        
        return script


# Global instance
ai_generator = AIContentGenerator()


def get_ai_generator() -> AIContentGenerator:
    """Get the global AI content generator instance"""
    return ai_generator
