"""
Enhanced logging system for MoneyPrinterTurboPro
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """Setup enhanced logging system"""
    
    try:
        # Remove default logger
        logger.remove()
        
        # Console logging
        if enable_console:
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
                level=log_level,
                colorize=True
            )
        
        # File logging
        if enable_file and log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                level=log_level,
                rotation="1 day",
                retention="7 days",
                compression="gz"
            )
        
        # Intercept standard logging
        class InterceptHandler(logging.Handler):
            def emit(self, record):
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno
                
                logger.opt(depth=6, exception=record.exc_info).log(
                    level, record.getMessage()
                )
        
        # Replace standard logging handlers
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        
        # Set specific logger levels
        for name in logging.root.manager.loggerDict:
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True
        
        logger.info("✅ Logging system initialized successfully")
        
    except Exception as e:
        # Fallback to basic logging if setup fails
        print(f"Warning: Logging setup failed: {e}")
        logger.add(sys.stdout, level="INFO")


def get_logger(name: str = None):
    """Get logger instance with context"""
    return logger.bind(name=name)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    logger.info(f"Performance: {operation} completed in {duration:.3f}s", **kwargs)


def log_security(event: str, user_id: str = None, ip_address: str = None, **kwargs):
    """Log security events"""
    logger.info(f"Security: {event}", user_id=user_id, ip_address=ip_address, **kwargs)


def log_business(operation: str, user_id: str = None, **kwargs):
    """Log business operations"""
    logger.info(f"Business: {operation}", user_id=user_id, **kwargs)


def log_error(error: Exception, context: str = None, user_id: str = None, **kwargs):
    """Log errors with context"""
    logger.error(f"Error in {context}: {str(error)}", user_id=user_id, **kwargs, exception=error)


def log_api_request(method: str, path: str, status_code: int, duration: float, **kwargs):
    """Log API request details"""
    level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
    logger.log(level, f"API {method} {path} - {status_code} ({duration:.3f}s)", **kwargs)
