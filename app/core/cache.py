"""
Cache initialization and management for MoneyPrinterTurboPro
"""

import os
from pathlib import Path
from typing import Optional, Any, Dict
from loguru import logger

from .config import settings


def init_cache():
    """Initialize cache system"""
    try:
        # Create cache directories
        cache_dir = Path(settings.cache.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create memory cache directory
        memory_cache_dir = cache_dir / "memory"
        memory_cache_dir.mkdir(exist_ok=True)
        
        # Create disk cache directory
        disk_cache_dir = cache_dir / "disk"
        disk_cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"✅ Cache initialized: {cache_dir}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache initialization failed: {e}")
        return False


def get_cache_dir() -> Path:
    """Get cache directory path"""
    return Path(settings.cache.cache_dir)


def is_cache_available() -> bool:
    """Check if cache is available"""
    try:
        cache_dir = Path(settings.cache.cache_dir)
        return cache_dir.exists() and cache_dir.is_dir()
    except Exception:
        return False


def clear_cache():
    """Clear all cache data"""
    try:
        cache_dir = Path(settings.cache.cache_dir)
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("✅ Cache cleared successfully")
            return True
    except Exception as e:
        logger.error(f"❌ Cache clearing failed: {e}")
        return False


def get_cache_info() -> Dict[str, Any]:
    """Get cache information and statistics"""
    try:
        cache_dir = Path(settings.cache.cache_dir)
        if not cache_dir.exists():
            return {"status": "not_initialized"}
        
        # Calculate cache size
        total_size = 0
        file_count = 0
        
        for file_path in cache_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        return {
            "status": "active",
            "cache_dir": str(cache_dir),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "memory_cache_enabled": settings.cache.enable_memory_cache,
            "disk_cache_enabled": settings.cache.enable_disk_cache
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get cache info: {e}")
        return {"status": "error", "error": str(e)}
