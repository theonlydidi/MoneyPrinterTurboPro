"""
Database initialization and management for MoneyPrinterTurboPro
"""

import os
from pathlib import Path
from typing import Optional
from loguru import logger
import time

from .config import settings


def init_database():
    """Initialize database connection and create tables if needed"""
    try:
        # For now, just create the database directory and basic structure
        # This is a simplified version - in production you'd use SQLAlchemy + Alembic
        
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        db_dir = db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Database initialized: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def get_database_url() -> str:
    """Get database URL from settings"""
    return settings.database_url


def is_database_available() -> bool:
    """Check if database is available and accessible"""
    try:
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        return db_path.exists() or db_path.parent.exists()
    except Exception:
        return False


def create_database_backup() -> Optional[str]:
    """Create a backup of the database"""
    try:
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        if not db_path.exists():
            return None
            
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"db_backup_{int(time.time())}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        
        logger.info(f"✅ Database backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        logger.error(f"❌ Database backup failed: {e}")
        return None
