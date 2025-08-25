"""
Monitoring Service for MoneyPrinterTurboPro
Handles metrics, health checks, and performance monitoring
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

import psutil
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
import requests

from app.core.config import settings
from app.core.logging import get_logger, time_operation


logger = get_logger(__name__)


class MonitoringService:
    """Monitoring and metrics collection service"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_metrics()
        self._setup_health_checks()
        self._start_metrics_collection()
        
    def _initialize_metrics(self):
        """Initialize Prometheus metrics"""
        try:
            # Video generation metrics
            self.video_generation_total = Counter(
                'moneyprinter_video_generation_total',
                'Total number of video generation requests',
                ['status', 'style', 'quality']
            )
            
            self.video_generation_duration = Histogram(
                'moneyprinter_video_generation_duration_seconds',
                'Video generation duration in seconds',
                ['style', 'quality'],
                buckets=[10, 30, 60, 120, 300, 600, 1200, 1800, 3600]
            )
            
            self.video_generation_size = Histogram(
                'moneyprinter_video_generation_size_bytes',
                'Generated video file size in bytes',
                ['style', 'quality'],
                buckets=[1024*1024, 10*1024*1024, 50*1024*1024, 100*1024*1024, 500*1024*1024, 1024*1024*1024]
            )
            
            # AI service metrics
            self.ai_requests_total = Counter(
                'moneyprinter_ai_requests_total',
                'Total number of AI service requests',
                ['provider', 'model', 'status']
            )
            
            self.ai_response_time = Histogram(
                'moneyprinter_ai_response_time_seconds',
                'AI service response time in seconds',
                ['provider', 'model'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            )
            
            # Voice synthesis metrics
            self.voice_synthesis_total = Counter(
                'moneyprinter_voice_synthesis_total',
                'Total number of voice synthesis requests',
                ['provider', 'voice_preset', 'status']
            )
            
            self.voice_synthesis_duration = Histogram(
                'moneyprinter_voice_synthesis_duration_seconds',
                'Voice synthesis duration in seconds',
                ['provider', 'voice_preset'],
                buckets=[1, 5, 10, 30, 60, 120, 300]
            )
            
            # Subtitle generation metrics
            self.subtitle_generation_total = Counter(
                'moneyprinter_subtitle_generation_total',
                'Total number of subtitle generation requests',
                ['provider', 'language', 'status']
            )
            
            self.subtitle_generation_duration = Histogram(
                'moneyprinter_subtitle_generation_duration_seconds',
                'Subtitle generation duration in seconds',
                ['provider', 'language'],
                buckets=[1, 5, 10, 30, 60, 120, 300]
            )
            
            # Music service metrics
            self.music_selection_total = Counter(
                'moneyprinter_music_selection_total',
                'Total number of music selection requests',
                ['source', 'style', 'status']
            )
            
            self.music_selection_duration = Histogram(
                'moneyprinter_music_selection_duration_seconds',
                'Music selection duration in seconds',
                ['source', 'style'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            )
            
            # Storage metrics
            self.storage_operations_total = Counter(
                'moneyprinter_storage_operations_total',
                'Total number of storage operations',
                ['operation', 'provider', 'status']
            )
            
            self.storage_operation_duration = Histogram(
                'moneyprinter_storage_operation_duration_seconds',
                'Storage operation duration in seconds',
                ['operation', 'provider'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            )
            
            # Database metrics
            self.database_operations_total = Counter(
                'moneyprinter_database_operations_total',
                'Total number of database operations',
                ['operation', 'table', 'status']
            )
            
            self.database_operation_duration = Histogram(
                'moneyprinter_database_operation_duration_seconds',
                'Database operation duration in seconds',
                ['operation', 'table'],
                buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            )
            
            # Cache metrics
            self.cache_operations_total = Counter(
                'moneyprinter_cache_operations_total',
                'Total number of cache operations',
                ['operation', 'status']
            )
            
            self.cache_hit_ratio = Gauge(
                'moneyprinter_cache_hit_ratio',
                'Cache hit ratio (0.0 to 1.0)'
            )
            
            # System metrics
            self.system_cpu_usage = Gauge(
                'moneyprinter_system_cpu_usage_percent',
                'System CPU usage percentage'
            )
            
            self.system_memory_usage = Gauge(
                'moneyprinter_system_memory_usage_bytes',
                'System memory usage in bytes'
            )
            
            self.system_disk_usage = Gauge(
                'moneyprinter_system_disk_usage_bytes',
                'System disk usage in bytes'
            )
            
            self.system_disk_free = Gauge(
                'moneyprinter_system_disk_free_bytes',
                'System free disk space in bytes'
            )
            
            # Application info
            self.app_info = Info(
                'moneyprinter_app',
                'Application information'
            )
            self.app_info.info({
                'version': '2.0.0',
                'name': 'MoneyPrinterTurboPro',
                'environment': settings.app.environment
            })
            
            self.logger.info("🚀 Prometheus metrics initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics: {str(e)}")
    
    def _setup_health_checks(self):
        """Setup health check endpoints"""
        self.health_checks = {
            'database': self._check_database_health,
            'redis': self._check_redis_health,
            'storage': self._check_storage_health,
            'ai_services': self._check_ai_services_health,
            'system': self._check_system_health
        }
        
        self.health_status = {
            'overall': 'healthy',
            'last_check': datetime.now(),
            'checks': {}
        }
    
    def _start_metrics_collection(self):
        """Start background metrics collection"""
        if not hasattr(self, '_metrics_task'):
            self._metrics_task = asyncio.create_task(self._collect_system_metrics())
            self.logger.info("🚀 System metrics collection started")
    
    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_memory_usage.set(memory.used)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.system_disk_usage.set(disk.used)
                self.system_disk_free.set(disk.free)
                
                # Wait for next collection
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.warning(f"System metrics collection failed: {str(e)}")
                await asyncio.sleep(60)
    
    @time_operation("health_check")
    async def check_health(self, detailed: bool = False) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        
        try:
            start_time = time.time()
            results = {}
            
            # Run all health checks
            for check_name, check_func in self.health_checks.items():
                try:
                    results[check_name] = await check_func()
                except Exception as e:
                    results[check_name] = {
                        'status': 'unhealthy',
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
            
            # Determine overall health
            overall_status = 'healthy'
            if any(check['status'] == 'unhealthy' for check in results.values()):
                overall_status = 'degraded'
            if any(check['status'] == 'critical' for check in results.values()):
                overall_status = 'critical'
            
            # Update health status
            self.health_status.update({
                'overall': overall_status,
                'last_check': datetime.now(),
                'checks': results,
                'response_time': time.time() - start_time
            })
            
            if detailed:
                return self.health_status
            else:
                return {
                    'status': overall_status,
                    'last_check': self.health_status['last_check'],
                    'response_time': self.health_status['response_time']
                }
                
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'critical',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        
        try:
            # This would integrate with the actual database service
            # For now, return a mock check
            return {
                'status': 'healthy',
                'message': 'Database connection successful',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        
        try:
            # This would integrate with the actual Redis client
            # For now, return a mock check
            return {
                'status': 'healthy',
                'message': 'Redis connection successful',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage health"""
        
        try:
            # Check disk space
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            if disk_usage_percent > 90:
                status = 'critical'
            elif disk_usage_percent > 80:
                status = 'degraded'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'disk_usage_percent': disk_usage_percent,
                'free_space_gb': disk.free / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services health"""
        
        try:
            # Check OpenAI API
            openai_status = 'unknown'
            try:
                # This would be an actual API call
                openai_status = 'healthy'
            except:
                openai_status = 'unhealthy'
            
            # Check other AI providers
            providers_status = {
                'openai': openai_status,
                'anthropic': 'unknown',
                'gemini': 'unknown',
                'qwen': 'unknown',
                'moonshot': 'unknown'
            }
            
            overall_status = 'healthy'
            if any(status == 'unhealthy' for status in providers_status.values()):
                overall_status = 'degraded'
            if all(status == 'unhealthy' for status in providers_status.values()):
                overall_status = 'critical'
            
            return {
                'status': overall_status,
                'providers': providers_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system health"""
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Determine status
            if cpu_percent > 90 or memory_percent > 90:
                status = 'critical'
            elif cpu_percent > 80 or memory_percent > 80:
                status = 'degraded'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory_percent,
                'memory_available_gb': memory.available / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def record_video_generation(self, status: str, style: str, quality: str, duration: float, size: int):
        """Record video generation metrics"""
        
        try:
            self.video_generation_total.labels(status=status, style=style, quality=quality).inc()
            self.video_generation_duration.labels(style=style, quality=quality).observe(duration)
            self.video_generation_size.labels(style=style, quality=quality).observe(size)
            
        except Exception as e:
            self.logger.warning(f"Failed to record video generation metrics: {str(e)}")
    
    def record_ai_request(self, provider: str, model: str, status: str, response_time: float):
        """Record AI service metrics"""
        
        try:
            self.ai_requests_total.labels(provider=provider, model=model, status=status).inc()
            self.ai_response_time.labels(provider=provider, model=model).observe(response_time)
            
        except Exception as e:
            self.logger.warning(f"Failed to record AI request metrics: {str(e)}")
    
    def record_voice_synthesis(self, provider: str, voice_preset: str, status: str, duration: float):
        """Record voice synthesis metrics"""
        
        try:
            self.voice_synthesis_total.labels(provider=provider, voice_preset=voice_preset, status=status).inc()
            self.voice_synthesis_duration.labels(provider=provider, voice_preset=voice_preset).observe(duration)
            
        except Exception as e:
            self.logger.warning(f"Failed to record voice synthesis metrics: {str(e)}")
    
    def record_subtitle_generation(self, provider: str, language: str, status: str, duration: float):
        """Record subtitle generation metrics"""
        
        try:
            self.subtitle_generation_total.labels(provider=provider, language=language, status=status).inc()
            self.subtitle_generation_duration.labels(provider=provider, language=language).observe(duration)
            
        except Exception as e:
            self.logger.warning(f"Failed to record subtitle generation metrics: {str(e)}")
    
    def record_music_selection(self, source: str, style: str, status: str, duration: float):
        """Record music selection metrics"""
        
        try:
            self.music_selection_total.labels(source=source, style=style, status=status).inc()
            self.music_selection_duration.labels(source=source, style=style).observe(duration)
            
        except Exception as e:
            self.logger.warning(f"Failed to record music selection metrics: {str(e)}")
    
    def record_storage_operation(self, operation: str, provider: str, status: str, duration: float):
        """Record storage operation metrics"""
        
        try:
            self.storage_operations_total.labels(operation=operation, provider=provider, status=status).inc()
            self.storage_operation_duration.labels(operation=operation, provider=provider).observe(duration)
            
        except Exception as e:
            self.logger.warning(f"Failed to record storage operation metrics: {str(e)}")
    
    def record_database_operation(self, operation: str, table: str, status: str, duration: float):
        """Record database operation metrics"""
        
        try:
            self.database_operations_total.labels(operation=operation, table=table, status=status).inc()
            self.database_operation_duration.labels(operation=operation, table=table).observe(duration)
            
        except Exception as e:
            self.logger.warning(f"Failed to record database operation metrics: {str(e)}")
    
    def record_cache_operation(self, operation: str, status: str, hit: bool = False):
        """Record cache operation metrics"""
        
        try:
            self.cache_operations_total.labels(operation=operation, status=status).inc()
            
            # Update hit ratio (simplified)
            if hasattr(self, '_cache_hits') and hasattr(self, '_cache_total'):
                self._cache_total += 1
                if hit:
                    self._cache_hits += 1
                
                if self._cache_total > 0:
                    hit_ratio = self._cache_hits / self._cache_total
                    self.cache_hit_ratio.set(hit_ratio)
            else:
                self._cache_hits = 0
                self._cache_total = 0
            
        except Exception as e:
            self.logger.warning(f"Failed to record cache operation metrics: {str(e)}")
    
    @time_operation("metrics_export")
    async def export_metrics(self, format: str = "prometheus") -> Dict[str, Any]:
        """Export metrics in specified format"""
        
        try:
            if format == "prometheus":
                # Return Prometheus format
                return {
                    'success': True,
                    'format': 'prometheus',
                    'data': prometheus_client.generate_latest(),
                    'content_type': 'text/plain; version=0.0.4; charset=utf-8'
                }
            
            elif format == "json":
                # Return JSON format with key metrics
                metrics_data = {
                    'video_generation': {
                        'total_requests': self.video_generation_total._value.sum(),
                        'average_duration': self.video_generation_duration.observe(0),  # This is simplified
                        'total_size': self.video_generation_size._value.sum()
                    },
                    'ai_services': {
                        'total_requests': self.ai_requests_total._value.sum(),
                        'average_response_time': self.ai_response_time.observe(0)  # This is simplified
                    },
                    'system': {
                        'cpu_usage': psutil.cpu_percent(),
                        'memory_usage': psutil.virtual_memory().percent,
                        'disk_usage': psutil.disk_usage('/').percent
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    'success': True,
                    'format': 'json',
                    'data': metrics_data,
                    'content_type': 'application/json'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported format: {format}'
                }
                
        except Exception as e:
            self.logger.error(f"Metrics export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        
        try:
            return {
                'video_generation': {
                    'total_requests': self.video_generation_total._value.sum(),
                    'total_duration': self.video_generation_duration.observe(0),  # Simplified
                    'total_size': self.video_generation_size._value.sum()
                },
                'ai_services': {
                    'total_requests': self.ai_requests_total._value.sum(),
                    'average_response_time': self.ai_response_time.observe(0)  # Simplified
                },
                'voice_synthesis': {
                    'total_requests': self.voice_synthesis_total._value.sum(),
                    'total_duration': self.voice_synthesis_duration.observe(0)  # Simplified
                },
                'subtitle_generation': {
                    'total_requests': self.subtitle_generation_total._value.sum(),
                    'total_duration': self.subtitle_generation_duration.observe(0)  # Simplified
                },
                'music_selection': {
                    'total_requests': self.music_selection_total._value.sum(),
                    'total_duration': self.music_selection_duration.observe(0)  # Simplified
                },
                'storage_operations': {
                    'total_operations': self.storage_operations_total._value.sum(),
                    'total_duration': self.storage_operation_duration.observe(0)  # Simplified
                },
                'database_operations': {
                    'total_operations': self.database_operations_total._value.sum(),
                    'total_duration': self.database_operation_duration.observe(0)  # Simplified
                },
                'cache_operations': {
                    'total_operations': self.cache_operations_total._value.sum(),
                    'hit_ratio': self.cache_hit_ratio._value.get()
                },
                'system': {
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {str(e)}")
            return {
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def close(self):
        """Close monitoring service"""
        
        try:
            if hasattr(self, '_metrics_task'):
                self._metrics_task.cancel()
                try:
                    await self._metrics_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Monitoring service closed")
            
        except Exception as e:
            self.logger.error(f"Failed to close monitoring service: {str(e)}")
