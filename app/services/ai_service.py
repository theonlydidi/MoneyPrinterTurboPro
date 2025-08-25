"""
AI Service for MoneyPrinterTurboPro
Handles multiple LLM providers with intelligent fallbacks and prompt engineering
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Tuple
from pathlib import Path

import openai
import anthropic
import google.generativeai as genai
from dashscope import Generation
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger, time_operation, log_api_request
from app.models.video import VideoRequest, VideoStyle, VideoQuality


logger = get_logger(__name__)


class AIService:
    """AI service for script generation and enhancement"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_providers()
        self._load_prompts()
        
    def _initialize_providers(self):
        """Initialize AI providers with API keys"""
        # OpenAI
        if settings.api_keys.openai_api_key:
            openai.api_key = settings.api_keys.openai_api_key
            self.openai_available = True
        else:
            self.openai_available = False
            
        # Anthropic
        if settings.api_keys.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.api_keys.anthropic_api_key
            )
            self.anthropic_available = True
        else:
            self.anthropic_available = False
            
        # Google Gemini
        if settings.api_keys.gemini_api_key:
            genai.configure(api_key=settings.api_keys.gemini_api_key)
            self.gemini_available = True
        else:
            self.gemini_available = False
            
        # DashScope (Qwen)
        if settings.api_keys.qwen_api_key:
            self.qwen_available = True
        else:
            self.qwen_available = False
            
        # Moonshot
        if settings.api_keys.moonshot_api_key:
            self.moonshot_available = True
        else:
            self.moonshot_available = False
            
        # Ollama
        if settings.api_keys.ollama_base_url:
            self.ollama_available = True
        else:
            self.ollama_available = False
            
        # G4F (Free tier)
        self.g4f_available = True
        
        self.logger.info(f"AI Providers initialized: OpenAI={self.openai_available}, "
                        f"Anthropic={self.anthropic_available}, Gemini={self.gemini_available}")
    
    def _load_prompts(self):
        """Load prompt templates"""
        self.prompts = {
            "script_generation": {
                "system": """You are an expert video script writer and content creator. 
                Your task is to create engaging, professional video scripts based on user requirements.
                
                Guidelines:
                - Create compelling narratives that engage viewers
                - Structure content with clear introduction, body, and conclusion
                - Use conversational, accessible language
                - Include specific details and examples
                - Optimize for the specified duration
                - Match the requested style and tone
                - Ensure logical flow and transitions
                
                Output format: Return only the script text, no additional formatting or explanations.""",
                
                "user_template": """Create a {duration}-second video script about: {description}
                
                Style: {style}
                Quality: {quality}
                Target audience: {audience}
                Tone: {tone}
                
                Additional requirements: {additional_requirements}"""
            },
            
            "script_enhancement": {
                "system": """You are an expert video script editor and enhancer.
                Your task is to improve existing scripts by making them more engaging, clear, and professional.
                
                Enhancement focus:
                - Improve clarity and flow
                - Add engaging hooks and transitions
                - Enhance emotional impact
                - Optimize for video format
                - Maintain original intent and message
                
                Output format: Return only the enhanced script text.""",
                
                "user_template": """Enhance this video script to make it more engaging and professional:
                
                Original script: {original_script}
                
                Target duration: {target_duration} seconds
                Style: {style}
                Enhancement focus: {focus_areas}"""
            },
            
            "content_analysis": {
                "system": """You are an expert content analyst specializing in video content.
                Analyze the given content and provide insights for optimization.
                
                Analysis areas:
                - Content structure and flow
                - Engagement potential
                - Target audience alignment
                - SEO and discoverability
                - Brand consistency
                
                Output format: JSON with analysis results."""
            }
        }
    
    @time_operation("ai_script_generation")
    async def generate_script(
        self,
        request: VideoRequest,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate video script using AI"""
        
        try:
            # Prepare prompt
            prompt_data = self._prepare_script_prompt(request)
            
            # Try providers in order of preference
            providers = self._get_provider_priority(request.ai_model)
            
            for provider in providers:
                try:
                    result = await self._generate_with_provider(
                        provider, prompt_data, request
                    )
                    if result and result.get('success'):
                        return {
                            'success': True,
                            'script': result['script'],
                            'provider': provider,
                            'metadata': result.get('metadata', {}),
                            'generation_time': result.get('generation_time', 0)
                        }
                except Exception as e:
                    self.logger.warning(f"Provider {provider} failed: {str(e)}")
                    continue
            
            # If all providers fail, return error
            raise Exception("All AI providers failed to generate script")
            
        except Exception as e:
            self.logger.error(f"Script generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _prepare_script_prompt(self, request: VideoRequest) -> Dict[str, Any]:
        """Prepare prompt data for script generation"""
        
        # Determine audience and tone based on style
        style_mapping = {
            VideoStyle.PROFESSIONAL: {"audience": "business professionals", "tone": "formal and authoritative"},
            VideoStyle.CREATIVE: {"audience": "creative professionals", "tone": "innovative and inspiring"},
            VideoStyle.MINIMALIST: {"audience": "design-conscious viewers", "tone": "clean and focused"},
            VideoStyle.DYNAMIC: {"audience": "young professionals", "tone": "energetic and engaging"},
            VideoStyle.CORPORATE: {"audience": "corporate stakeholders", "tone": "professional and trustworthy"},
            VideoStyle.SOCIAL_MEDIA: {"audience": "social media users", "tone": "casual and relatable"},
            VideoStyle.EDUCATIONAL: {"audience": "students and learners", "tone": "clear and educational"},
            VideoStyle.ENTERTAINMENT: {"audience": "general audience", "tone": "entertaining and engaging"}
        }
        
        style_info = style_mapping.get(request.style, style_mapping[VideoStyle.PROFESSIONAL])
        
        # Calculate words per second (average speaking rate: 150 words/minute)
        target_words = int((request.duration / 60) * 150)
        
        return {
            'duration': request.duration,
            'description': request.description,
            'style': request.style.value,
            'quality': request.quality.value,
            'audience': style_info['audience'],
            'tone': style_info['tone'],
            'target_words': target_words,
            'additional_requirements': self._format_additional_requirements(request)
        }
    
    def _format_additional_requirements(self, request: VideoRequest) -> str:
        """Format additional requirements for the prompt"""
        requirements = []
        
        if request.custom_prompts:
            requirements.append(f"Custom prompts: {', '.join(request.custom_prompts)}")
        
        if request.exclude_keywords:
            requirements.append(f"Avoid keywords: {', '.join(request.exclude_keywords)}")
        
        if request.language != "en":
            requirements.append(f"Language: {request.language}")
        
        if request.tags:
            requirements.append(f"Include themes: {', '.join(request.tags)}")
        
        return "; ".join(requirements) if requirements else "None"
    
    def _get_provider_priority(self, preferred_model: str) -> List[str]:
        """Get prioritized list of providers based on preferred model"""
        
        # Define provider priorities
        provider_priorities = {
            'gpt-4': ['openai', 'anthropic', 'gemini', 'qwen', 'moonshot', 'ollama', 'g4f'],
            'gpt-3.5': ['openai', 'anthropic', 'gemini', 'qwen', 'moonshot', 'ollama', 'g4f'],
            'claude': ['anthropic', 'openai', 'gemini', 'qwen', 'moonshot', 'ollama', 'g4f'],
            'gemini': ['gemini', 'openai', 'anthropic', 'qwen', 'moonshot', 'ollama', 'g4f'],
            'qwen': ['qwen', 'openai', 'anthropic', 'gemini', 'moonshot', 'ollama', 'g4f'],
            'moonshot': ['moonshot', 'openai', 'anthropic', 'gemini', 'qwen', 'ollama', 'g4f'],
            'ollama': ['ollama', 'openai', 'anthropic', 'gemini', 'qwen', 'moonshot', 'g4f']
        }
        
        # Get priority list for preferred model, fallback to default
        priority = provider_priorities.get(preferred_model, provider_priorities['gpt-4'])
        
        # Filter to only available providers
        available_providers = []
        for provider in priority:
            if getattr(self, f"{provider}_available", False):
                available_providers.append(provider)
        
        # Always add G4F as fallback
        if 'g4f' not in available_providers:
            available_providers.append('g4f')
        
        return available_providers
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_with_provider(
        self,
        provider: str,
        prompt_data: Dict[str, Any],
        request: VideoRequest
    ) -> Dict[str, Any]:
        """Generate content with specific provider"""
        
        start_time = time.time()
        
        try:
            if provider == 'openai':
                return await self._generate_openai(prompt_data, request)
            elif provider == 'anthropic':
                return await self._generate_anthropic(prompt_data, request)
            elif provider == 'gemini':
                return await self._generate_gemini(prompt_data, request)
            elif provider == 'qwen':
                return await self._generate_qwen(prompt_data, request)
            elif provider == 'moonshot':
                return await self._generate_moonshot(prompt_data, request)
            elif provider == 'ollama':
                return await self._generate_ollama(prompt_data, request)
            elif provider == 'g4f':
                return await self._generate_g4f(prompt_data, request)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Provider {provider} generation failed: {str(e)}")
            raise
    
    async def _generate_openai(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using OpenAI"""
        
        system_prompt = self.prompts['script_generation']['system']
        user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4" if "gpt-4" in request.ai_model else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=prompt_data['target_words'] * 2,  # Allow for longer generation
            temperature=0.7,
            top_p=0.9
        )
        
        script = response.choices[0].message.content.strip()
        
        return {
            'success': True,
            'script': script,
            'metadata': {
                'model': response.model,
                'usage': response.usage.dict() if response.usage else {},
                'finish_reason': response.choices[0].finish_reason
            }
        }
    
    async def _generate_anthropic(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using Anthropic Claude"""
        
        system_prompt = self.prompts['script_generation']['system']
        user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=prompt_data['target_words'] * 2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        script = response.content[0].text.strip()
        
        return {
            'success': True,
            'script': script,
            'metadata': {
                'model': response.model,
                'usage': response.usage.dict() if response.usage else {},
                'stop_reason': response.stop_reason
            }
        }
    
    async def _generate_gemini(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using Google Gemini"""
        
        system_prompt = self.prompts['script_generation']['system']
        user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
        
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = await model.generate_content_async(full_prompt)
        
        script = response.text.strip()
        
        return {
            'success': True,
            'script': script,
            'metadata': {
                'model': 'gemini-1.5-pro',
                'finish_reason': response.candidates[0].finish_reason if response.candidates else None
            }
        }
    
    async def _generate_qwen(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using DashScope Qwen"""
        
        system_prompt = self.prompts['script_generation']['system']
        user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = Generation.call(
            model='qwen-max',
            messages=messages,
            result_format='message',
            max_tokens=prompt_data['target_words'] * 2
        )
        
        if response.status_code == 200:
            script = response.output.choices[0].message.content.strip()
            return {
                'success': True,
                'script': script,
                'metadata': {
                    'model': 'qwen-max',
                    'usage': response.usage.dict() if hasattr(response, 'usage') else {}
                }
            }
        else:
            raise Exception(f"Qwen API error: {response.message}")
    
    async def _generate_moonshot(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using Moonshot AI"""
        
        system_prompt = self.prompts['script_generation']['system']
        user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
        
        headers = {
            "Authorization": f"Bearer {settings.api_keys.moonshot_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": prompt_data['target_words'] * 2,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            script = result['choices'][0]['message']['content'].strip()
            return {
                'success': True,
                'script': script,
                'metadata': {
                    'model': 'moonshot-v1-8k',
                    'usage': result.get('usage', {})
                }
            }
        else:
            raise Exception(f"Moonshot API error: {response.status_code} - {response.text}")
    
    async def _generate_ollama(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using Ollama (local)"""
        
        system_prompt = self.prompts['script_generation']['system']
        user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
        
        data = {
            "model": "llama2:13b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        response = requests.post(
            f"{settings.api_keys.ollama_base_url}/api/chat",
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            script = result['message']['content'].strip()
            return {
                'success': True,
                'script': script,
                'metadata': {
                    'model': 'llama2:13b',
                    'provider': 'ollama'
                }
            }
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    async def _generate_g4f(self, prompt_data: Dict[str, Any], request: VideoRequest) -> Dict[str, Any]:
        """Generate using G4F (free tier fallback)"""
        
        try:
            import g4f
            
            system_prompt = self.prompts['script_generation']['system']
            user_prompt = self.prompts['script_generation']['user_template'].format(**prompt_data)
            
            # Combine prompts for G4F
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = await g4f.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": full_prompt}],
                provider=g4f.Provider.DeepAi
            )
            
            script = response.strip()
            
            return {
                'success': True,
                'script': script,
                'metadata': {
                    'model': 'gpt-3.5-turbo',
                    'provider': 'g4f',
                    'note': 'Free tier fallback'
                }
            }
            
        except ImportError:
            raise Exception("G4F not available for fallback generation")
        except Exception as e:
            raise Exception(f"G4F generation failed: {str(e)}")
    
    @time_operation("ai_script_enhancement")
    async def enhance_script(
        self,
        original_script: str,
        enhancement_focus: List[str],
        target_duration: int,
        style: VideoStyle
    ) -> Dict[str, Any]:
        """Enhance existing script using AI"""
        
        try:
            prompt_data = {
                'original_script': original_script,
                'target_duration': target_duration,
                'style': style.value,
                'focus_areas': ', '.join(enhancement_focus)
            }
            
            # Use the same provider selection logic
            providers = self._get_provider_priority('gpt-4')
            
            for provider in providers:
                try:
                    result = await self._enhance_with_provider(provider, prompt_data)
                    if result and result.get('success'):
                        return {
                            'success': True,
                            'enhanced_script': result['script'],
                            'provider': provider,
                            'enhancements_applied': enhancement_focus
                        }
                except Exception as e:
                    self.logger.warning(f"Provider {provider} enhancement failed: {str(e)}")
                    continue
            
            raise Exception("All AI providers failed to enhance script")
            
        except Exception as e:
            self.logger.error(f"Script enhancement failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _enhance_with_provider(self, provider: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance script with specific provider"""
        
        if provider == 'openai':
            return await self._enhance_openai(prompt_data)
        elif provider == 'anthropic':
            return await self._enhance_anthropic(prompt_data)
        # Add other providers as needed
        else:
            # Fallback to basic enhancement
            return await self._enhance_openai(prompt_data)
    
    async def _enhance_openai(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance script using OpenAI"""
        
        system_prompt = self.prompts['script_enhancement']['system']
        user_prompt = self.prompts['script_enhancement']['user_template'].format(**prompt_data)
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=len(prompt_data['original_script']) * 2,
            temperature=0.7
        )
        
        enhanced_script = response.choices[0].message.content.strip()
        
        return {
            'success': True,
            'script': enhanced_script
        }
    
    async def _enhance_anthropic(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance script using Anthropic"""
        
        system_prompt = self.prompts['script_enhancement']['system']
        user_prompt = self.prompts['script_enhancement']['user_template'].format(**prompt_data)
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=len(prompt_data['original_script']) * 2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        enhanced_script = response.content[0].text.strip()
        
        return {
            'success': True,
            'script': enhanced_script
        }
    
    @time_operation("ai_content_analysis")
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze content for optimization insights"""
        
        try:
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following content and provide optimization insights:
            
            Content: {content[:1000]}...
            
            Analysis type: {analysis_type}
            
            Provide analysis in JSON format with the following structure:
            {{
                "content_structure": "assessment of content organization",
                "engagement_potential": "score from 1-10 with explanation",
                "target_audience": "identified target audience",
                "seo_opportunities": "SEO improvement suggestions",
                "brand_consistency": "brand alignment assessment",
                "recommendations": ["list of specific improvements"]
            }}
            """
            
            # Use OpenAI for analysis (most reliable for structured output)
            if self.openai_available:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a content analysis expert. Provide analysis in valid JSON format only."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                analysis_text = response.choices[0].message.content.strip()
                
                # Parse JSON response
                try:
                    analysis = json.loads(analysis_text)
                    return {
                        'success': True,
                        'analysis': analysis,
                        'provider': 'openai'
                    }
                except json.JSONDecodeError:
                    # Fallback to text parsing
                    return {
                        'success': True,
                        'analysis': {'raw_analysis': analysis_text},
                        'provider': 'openai'
                    }
            
            else:
                # Fallback to basic analysis
                return {
                    'success': True,
                    'analysis': {
                        'content_structure': 'Basic analysis not available',
                        'engagement_potential': 'Analysis requires AI provider',
                        'recommendations': ['Enable AI provider for detailed analysis']
                    },
                    'provider': 'fallback'
                }
                
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get list of available AI providers"""
        return {
            'openai': self.openai_available,
            'anthropic': self.anthropic_available,
            'gemini': self.gemini_available,
            'qwen': self.qwen_available,
            'moonshot': self.moonshot_available,
            'ollama': self.ollama_available,
            'g4f': self.g4f_available
        }
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all providers"""
        status = {}
        
        for provider in ['openai', 'anthropic', 'gemini', 'qwen', 'moonshot', 'ollama', 'g4f']:
            available = getattr(self, f"{provider}_available", False)
            status[provider] = {
                'available': available,
                'status': 'active' if available else 'unavailable',
                'last_check': datetime.now().isoformat()
            }
        
        return status
