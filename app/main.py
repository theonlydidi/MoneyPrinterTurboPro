"""
Main FastAPI Application for MoneyPrinterTurboPro
Provides REST API endpoints for video generation
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from app.core.config import settings
from app.core.logging import get_logger, time_operation
from app.models.video import (
    VideoRequest, VideoResponse, VideoTemplate, VideoBatchRequest, 
    VideoAnalytics, VideoStatus, VideoQuality, VideoStyle
)
from app.services.video_generator import VideoGeneratorService
from app.services.database_service import DatabaseService
from app.services.monitoring_service import MonitoringService
from app.services.storage_service import StorageManager


logger = get_logger(__name__)
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info("🚀 Starting MoneyPrinterTurboPro API...")
    
    # Initialize services
    app.state.video_generator = VideoGeneratorService()
    app.state.database_service = DatabaseService()
    app.state.monitoring_service = MonitoringService()
    app.state.storage_manager = StorageManager()
    
    logger.info("✅ All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MoneyPrinterTurboPro API...")
    
    # Close services
    await app.state.video_generator.close()
    await app.state.database_service.close()
    await app.state.monitoring_service.close()
    
    logger.info("✅ All services closed successfully")


# Create FastAPI app
app = FastAPI(
    title="MoneyPrinterTurboPro API",
    description="Professional AI-powered video generation API",
    version="2.0.0",
    docs_url="/docs" if settings.development.debug else None,
    redoc_url="/redoc" if settings.development.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Dependency functions
async def get_video_generator() -> VideoGeneratorService:
    """Get video generator service"""
    return app.state.video_generator


async def get_database_service() -> DatabaseService:
    """Get database service"""
    return app.state.database_service


async def get_monitoring_service() -> MonitoringService:
    """Get monitoring service"""
    return app.state.monitoring_service


async def get_storage_manager() -> StorageManager:
    """Get storage manager"""
    return app.state.storage_manager


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API key"""
    api_key = credentials.credentials
    
    # Simple API key validation (in production, use proper authentication)
    if api_key != settings.api_keys.master_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        monitoring_service = get_monitoring_service()
        health_status = await monitoring_service.check_health()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get Prometheus metrics"""
    try:
        monitoring_service = get_monitoring_service()
        metrics = await monitoring_service.export_metrics("prometheus")
        return StreamingResponse(
            iter([metrics['data']]),
            media_type=metrics['content_type']
        )
    except Exception as e:
        logger.error(f"Metrics export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Video generation endpoints
@app.post("/videos/generate", response_model=VideoResponse, tags=["Video Generation"])
async def generate_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None,
    template_id: Optional[int] = None,
    video_generator: VideoGeneratorService = Depends(get_video_generator)
):
    """Generate a single video"""
    
    try:
        # Start video generation in background
        result = await video_generator.generate_video(request, user_id, template_id)
        
        if result['success']:
            return result['response']
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['error']
            )
            
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/videos/generate/batch", tags=["Video Generation"])
async def generate_batch_videos(
    batch_request: VideoBatchRequest,
    user_id: Optional[str] = None,
    video_generator: VideoGeneratorService = Depends(get_video_generator)
):
    """Generate multiple videos in batch"""
    
    try:
        result = await video_generator.generate_batch_videos(batch_request, user_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['error']
            )
            
    except Exception as e:
        logger.error(f"Batch video generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/videos/{request_id}/status", tags=["Video Generation"])
async def get_video_status(
    request_id: int,
    video_generator: VideoGeneratorService = Depends(get_video_generator)
):
    """Get video generation status"""
    
    try:
        result = await video_generator.get_generation_status(request_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Video request not found')
            )
            
    except Exception as e:
        logger.error(f"Failed to get video status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/videos/{request_id}/cancel", tags=["Video Generation"])
async def cancel_video_generation(
    request_id: int,
    video_generator: VideoGeneratorService = Depends(get_video_generator)
):
    """Cancel video generation"""
    
    try:
        result = await video_generator.cancel_generation(request_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to cancel generation')
            )
            
    except Exception as e:
        logger.error(f"Failed to cancel video generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Video management endpoints
@app.get("/videos", tags=["Video Management"])
async def list_videos(
    user_id: Optional[str] = None,
    status: Optional[VideoStatus] = None,
    limit: int = 50,
    offset: int = 0,
    database_service: DatabaseService = Depends(get_database_service)
):
    """List video requests"""
    
    try:
        result = await database_service.list_video_requests(
            user_id=user_id,
            status=status.value if status else None,
            limit=limit,
            offset=offset
        )
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to list videos')
            )
            
    except Exception as e:
        logger.error(f"Failed to list videos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/videos/{request_id}", tags=["Video Management"])
async def get_video(
    request_id: int,
    database_service: DatabaseService = Depends(get_database_service)
):
    """Get video request details"""
    
    try:
        result = await database_service.get_video_request(request_id)
        
        if result['success']:
            return result['data']
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Video request not found')
            )
            
    except Exception as e:
        logger.error(f"Failed to get video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Template management endpoints
@app.post("/templates", tags=["Templates"])
async def create_template(
    template: VideoTemplate,
    user_id: Optional[str] = None,
    database_service: DatabaseService = Depends(get_database_service)
):
    """Create video template"""
    
    try:
        result = await database_service.save_video_template(template, user_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to create template')
            )
            
    except Exception as e:
        logger.error(f"Failed to create template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Analytics endpoints
@app.post("/analytics", tags=["Analytics"])
async def save_analytics(
    analytics: VideoAnalytics,
    database_service: DatabaseService = Depends(get_database_service)
):
    """Save video analytics"""
    
    try:
        result = await database_service.save_video_analytics(analytics)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to save analytics')
            )
            
    except Exception as e:
        logger.error(f"Failed to save analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# System status endpoints
@app.get("/status", tags=["System"])
async def get_system_status(
    video_generator: VideoGeneratorService = Depends(get_video_generator)
):
    """Get system status"""
    
    try:
        return video_generator.get_service_status()
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/storage/status", tags=["System"])
async def get_storage_status(
    storage_manager: StorageManager = Depends(get_storage_manager)
):
    """Get storage status"""
    
    try:
        return storage_manager.get_storage_status()
    except Exception as e:
        logger.error(f"Failed to get storage status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": "HTTPException"
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MoneyPrinterTurboPro API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.development.debug,
        log_level="info"
    )
