"""
Database Service for MoneyPrinterTurboPro
Handles database operations, migrations, and caching
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as redis
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.core.logging import get_logger, time_operation
from app.models.video import VideoRequest, VideoResponse, VideoTemplate, VideoBatchRequest, VideoAnalytics


logger = get_logger(__name__)
Base = declarative_base()


class DatabaseService:
    """Database management with PostgreSQL and Redis"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_connections()
        self._setup_tables()
        self._initialize_cache()
        
    def _initialize_connections(self):
        """Initialize database connections"""
        # PostgreSQL
        try:
            # Sync engine for migrations
            self.sync_engine = create_engine(
                settings.database.postgres_url,
                echo=settings.development.debug,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Async engine for operations
            self.async_engine = create_async_engine(
                settings.database.postgres_url.replace('postgresql://', 'postgresql+asyncpg://'),
                echo=settings.development.debug,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Session factories
            self.SyncSession = sessionmaker(bind=self.sync_engine)
            self.AsyncSession = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.postgres_available = True
            self.logger.info("🚀 PostgreSQL database initialized")
            
        except Exception as e:
            self.logger.error(f"PostgreSQL initialization failed: {str(e)}")
            self.postgres_available = False
            
        # Redis
        try:
            self.redis_client = redis.from_url(
                settings.database.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self.redis_available = True
            self.logger.info("🚀 Redis cache initialized")
            
        except Exception as e:
            self.logger.error(f"Redis initialization failed: {str(e)}")
            self.redis_available = False
    
    def _setup_tables(self):
        """Setup database tables"""
        if not self.postgres_available:
            return
            
        try:
            # Create tables
            Base.metadata.create_all(self.sync_engine)
            
            # Run migrations if Alembic is available
            if os.path.exists("alembic.ini"):
                self._run_migrations()
                
        except Exception as e:
            self.logger.error(f"Table setup failed: {str(e)}")
    
    def _run_migrations(self):
        """Run database migrations"""
        try:
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            self.logger.info("✅ Database migrations completed")
            
        except Exception as e:
            self.logger.warning(f"Database migrations failed: {str(e)}")
    
    def _initialize_cache(self):
        """Initialize cache configuration"""
        self.cache_config = {
            'default_ttl': settings.database.cache_ttl_seconds,
            'video_ttl': 3600,  # 1 hour for video data
            'user_ttl': 1800,   # 30 minutes for user data
            'stats_ttl': 300,   # 5 minutes for statistics
            'batch_size': 100   # Batch size for bulk operations
        }
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session"""
        if not self.postgres_available:
            raise Exception("PostgreSQL not available")
            
        async with self.AsyncSession() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
    
    @time_operation("database_query")
    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch: bool = True
    ) -> Dict[str, Any]:
        """Execute raw SQL query"""
        
        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})
                
                if fetch:
                    rows = result.fetchall()
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                    return {
                        'success': True,
                        'data': data,
                        'row_count': len(data)
                    }
                else:
                    return {
                        'success': True,
                        'affected_rows': result.rowcount
                    }
                    
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_save")
    async def save_video_request(
        self,
        video_request: VideoRequest,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save video request to database"""
        
        try:
            async with self.get_session() as session:
                # Create video request record
                request_data = {
                    'user_id': user_id,
                    'title': video_request.title,
                    'description': video_request.description,
                    'duration': video_request.duration,
                    'style': video_request.style.value,
                    'quality': video_request.quality.value,
                    'voice_preset': video_request.voice_preset.value,
                    'background_music': video_request.background_music,
                    'music_intensity': video_request.music_intensity,
                    'aspect_ratio': video_request.aspect_ratio,
                    'transitions': video_request.transitions.value,
                    'ai_model': video_request.ai_model,
                    'language': video_request.language,
                    'custom_prompts': json.dumps(video_request.custom_prompts) if video_request.custom_prompts else None,
                    'exclude_keywords': json.dumps(video_request.exclude_keywords) if video_request.exclude_keywords else None,
                    'include_subtitles': video_request.include_subtitles,
                    'tags': json.dumps(video_request.tags) if video_request.tags else None,
                    'category': video_request.category,
                    'created_at': datetime.now(),
                    'status': 'pending'
                }
                
                query = """
                INSERT INTO video_requests (
                    user_id, title, description, duration, style, quality, voice_preset,
                    background_music, music_intensity, aspect_ratio, transitions, ai_model,
                    language, custom_prompts, exclude_keywords, include_subtitles, tags,
                    category, created_at, status
                ) VALUES (
                    :user_id, :title, :description, :duration, :style, :quality, :voice_preset,
                    :background_music, :music_intensity, :aspect_ratio, :transitions, :ai_model,
                    :language, :custom_prompts, :exclude_keywords, :include_subtitles, :tags,
                    :category, :created_at, :status
                ) RETURNING id
                """
                
                result = await session.execute(text(query), request_data)
                request_id = result.scalar()
                
                # Cache the request
                await self._cache_video_request(request_id, request_data)
                
                return {
                    'success': True,
                    'request_id': request_id,
                    'message': 'Video request saved successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to save video request: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_update")
    async def update_video_status(
        self,
        request_id: int,
        status: str,
        video_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update video request status"""
        
        try:
            async with self.get_session() as session:
                update_data = {
                    'request_id': request_id,
                    'status': status,
                    'updated_at': datetime.now()
                }
                
                if video_path:
                    update_data['video_path'] = video_path
                if metadata:
                    update_data['metadata'] = json.dumps(metadata)
                
                query = """
                UPDATE video_requests 
                SET status = :status, updated_at = :updated_at
                """
                
                if video_path:
                    query += ", video_path = :video_path"
                if metadata:
                    query += ", metadata = :metadata"
                
                query += " WHERE id = :request_id"
                
                result = await session.execute(text(query), update_data)
                
                if result.rowcount == 0:
                    return {
                        'success': False,
                        'error': 'Video request not found'
                    }
                
                # Update cache
                await self._update_cached_video_request(request_id, update_data)
                
                return {
                    'success': True,
                    'message': 'Video status updated successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to update video status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_fetch")
    async def get_video_request(
        self,
        request_id: int,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get video request by ID"""
        
        try:
            # Try cache first
            if use_cache and self.redis_available:
                cached_data = await self._get_cached_video_request(request_id)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache'
                    }
            
            # Query database
            async with self.get_session() as session:
                query = """
                SELECT * FROM video_requests WHERE id = :request_id
                """
                
                result = await session.execute(text(query), {'request_id': request_id})
                row = result.fetchone()
                
                if not row:
                    return {
                        'success': False,
                        'error': 'Video request not found'
                    }
                
                # Convert to dict
                data = dict(row._mapping)
                
                # Parse JSON fields
                for field in ['custom_prompts', 'exclude_keywords', 'tags', 'metadata']:
                    if data.get(field):
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            pass
                
                # Cache the result
                if self.redis_available:
                    await self._cache_video_request(request_id, data)
                
                return {
                    'success': True,
                    'data': data,
                    'source': 'database'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get video request: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("video_list")
    async def list_video_requests(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """List video requests with filters"""
        
        try:
            # Build cache key
            cache_key = f"video_requests:{user_id or 'all'}:{status or 'all'}:{limit}:{offset}"
            
            # Try cache first
            if use_cache and self.redis_available:
                cached_data = await self._get_cache(cache_key)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'source': 'cache'
                    }
            
            # Query database
            async with self.get_session() as session:
                query = "SELECT * FROM video_requests WHERE 1=1"
                params = {}
                
                if user_id:
                    query += " AND user_id = :user_id"
                    params['user_id'] = user_id
                
                if status:
                    query += " AND status = :status"
                    params['status'] = status
                
                query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
                params['limit'] = limit
                params['offset'] = offset
                
                result = await session.execute(text(query), params)
                rows = result.fetchall()
                
                # Convert to list of dicts
                data = []
                for row in rows:
                    row_data = dict(row._mapping)
                    
                    # Parse JSON fields
                    for field in ['custom_prompts', 'exclude_keywords', 'tags', 'metadata']:
                        if row_data.get(field):
                            try:
                                row_data[field] = json.loads(row_data[field])
                            except:
                                pass
                    
                    data.append(row_data)
                
                # Cache the result
                if self.redis_available:
                    await self._set_cache(cache_key, data, self.cache_config['video_ttl'])
                
                return {
                    'success': True,
                    'data': data,
                    'count': len(data),
                    'source': 'database'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to list video requests: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("template_save")
    async def save_video_template(
        self,
        template: VideoTemplate,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save video template"""
        
        try:
            async with self.get_session() as session:
                template_data = {
                    'user_id': user_id,
                    'name': template.name,
                    'description': template.description,
                    'style': template.style.value,
                    'quality': template.quality.value,
                    'voice_preset': template.voice_preset.value,
                    'background_music': template.background_music,
                    'music_intensity': template.music_intensity,
                    'aspect_ratio': template.aspect_ratio,
                    'transitions': template.transitions.value,
                    'ai_model': template.ai_model,
                    'language': template.language,
                    'custom_prompts': json.dumps(template.custom_prompts) if template.custom_prompts else None,
                    'exclude_keywords': json.dumps(template.exclude_keywords) if template.exclude_keywords else None,
                    'include_subtitles': template.include_subtitles,
                    'tags': json.dumps(template.tags) if template.tags else None,
                    'category': template.category,
                    'created_at': datetime.now()
                }
                
                query = """
                INSERT INTO video_templates (
                    user_id, name, description, style, quality, voice_preset,
                    background_music, music_intensity, aspect_ratio, transitions, ai_model,
                    language, custom_prompts, exclude_keywords, include_subtitles, tags,
                    category, created_at
                ) VALUES (
                    :user_id, :name, :description, :style, :quality, :voice_preset,
                    :background_music, :music_intensity, :aspect_ratio, :transitions, :ai_model,
                    :language, :custom_prompts, :exclude_keywords, :include_subtitles, :tags,
                    :category, :created_at
                ) RETURNING id
                """
                
                result = await session.execute(text(query), template_data)
                template_id = result.scalar()
                
                return {
                    'success': True,
                    'template_id': template_id,
                    'message': 'Video template saved successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to save video template: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("analytics_save")
    async def save_video_analytics(
        self,
        analytics: VideoAnalytics
    ) -> Dict[str, Any]:
        """Save video analytics"""
        
        try:
            async with self.get_session() as session:
                analytics_data = {
                    'video_id': analytics.video_id,
                    'user_id': analytics.user_id,
                    'views': analytics.views,
                    'likes': analytics.likes,
                    'shares': analytics.shares,
                    'comments': analytics.comments,
                    'watch_time': analytics.watch_time,
                    'completion_rate': analytics.completion_rate,
                    'engagement_score': analytics.engagement_score,
                    'demographics': json.dumps(analytics.demographics) if analytics.demographics else None,
                    'geographic_data': json.dumps(analytics.geographic_data) if analytics.geographic_data else None,
                    'device_data': json.dumps(analytics.device_data) if analytics.device_data else None,
                    'tracked_at': datetime.now()
                }
                
                query = """
                INSERT INTO video_analytics (
                    video_id, user_id, views, likes, shares, comments, watch_time,
                    completion_rate, engagement_score, demographics, geographic_data,
                    device_data, tracked_at
                ) VALUES (
                    :video_id, :user_id, :views, :likes, :shares, :comments, :watch_time,
                    :completion_rate, :engagement_score, :demographics, :geographic_data,
                    :device_data, :tracked_at
                ) RETURNING id
                """
                
                result = await session.execute(text(query), analytics_data)
                analytics_id = result.scalar()
                
                return {
                    'success': True,
                    'analytics_id': analytics_id,
                    'message': 'Video analytics saved successfully'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to save video analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @time_operation("cache_set")
    async def _set_cache(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set cache value"""
        
        if not self.redis_available:
            return False
            
        try:
            ttl = ttl or self.cache_config['default_ttl']
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis_client.setex(key, ttl, value)
            return True
            
        except Exception as e:
            self.logger.warning(f"Cache set failed: {str(e)}")
            return False
    
    @time_operation("cache_get")
    async def _get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        
        if not self.redis_available:
            return None
            
        try:
            value = await self.redis_client.get(key)
            
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Cache get failed: {str(e)}")
            return None
    
    async def _cache_video_request(
        self,
        request_id: int,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Cache video request data"""
        
        if not self.redis_available:
            return
            
        cache_key = f"video_request:{request_id}"
        ttl = ttl or self.cache_config['video_ttl']
        
        await self._set_cache(cache_key, data, ttl)
    
    async def _get_cached_video_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Get cached video request data"""
        
        if not self.redis_available:
            return None
            
        cache_key = f"video_request:{request_id}"
        return await self._get_cache(cache_key)
    
    async def _update_cached_video_request(
        self,
        request_id: int,
        update_data: Dict[str, Any]
    ):
        """Update cached video request data"""
        
        if not self.redis_available:
            return
            
        cache_key = f"video_request:{request_id}"
        cached_data = await self._get_cache(cache_key)
        
        if cached_data:
            cached_data.update(update_data)
            await self._set_cache(cache_key, cached_data, self.cache_config['video_ttl'])
    
    @time_operation("cache_clear")
    async def clear_cache(self, pattern: str = "*") -> Dict[str, Any]:
        """Clear cache by pattern"""
        
        if not self.redis_available:
            return {
                'success': False,
                'error': 'Redis not available'
            }
            
        try:
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
            
            return {
                'success': True,
                'cleared_keys': len(keys),
                'pattern': pattern
            }
            
        except Exception as e:
            self.logger.error(f"Cache clear failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database status and statistics"""
        
        try:
            status = {
                'postgres': {
                    'available': self.postgres_available,
                    'url': settings.database.postgres_url.split('@')[1] if '@' in settings.database.postgres_url else 'N/A'
                },
                'redis': {
                    'available': self.redis_available,
                    'url': settings.database.redis_url
                },
                'cache_config': self.cache_config
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get database status: {str(e)}")
            return {
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def close(self):
        """Close database connections"""
        
        try:
            if hasattr(self, 'async_engine'):
                await self.async_engine.dispose()
            
            if hasattr(self, 'sync_engine'):
                self.sync_engine.dispose()
                
            if hasattr(self, 'redis_client'):
                await self.redis_client.close()
                
            self.logger.info("Database connections closed")
            
        except Exception as e:
            self.logger.error(f"Failed to close database connections: {str(e)}")
