"""
FastAPI application creation for MoneyPrinterTurboPro
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from ..core.config import settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="MoneyPrinterTurboPro API",
        description="AI-Powered Video Generation Platform",
        version="2.0.0",
        docs_url="/docs" if settings.api.enable_docs else None,
        redoc_url="/redoc" if settings.api.enable_docs else None
    )
    
    # Add CORS middleware
    if settings.api.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add basic routes
    @app.get("/")
    async def root():
        return {"message": "MoneyPrinterTurboPro API", "version": "2.0.0"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "MoneyPrinterTurboPro"}
    
    @app.get("/api/v1/status")
    async def api_status():
        return {
            "status": "active",
            "version": "2.0.0",
            "features": {
                "video_generation": True,
                "ai_models": True,
                "plugins": settings.plugins.enable_plugins
            }
        }
    
    logger.info("✅ FastAPI application created successfully")
    return app
