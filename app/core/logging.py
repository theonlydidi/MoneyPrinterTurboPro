"""
Enhanced logging system for MoneyPrinterTurboPro
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from loguru._defaults import LOGURU_FORMAT


class StructuredFormatter:
    """Custom formatter for structured logging"""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        self.include_timestamp = include_timestamp
        self.include_level = include_timestamp
    
    def format(self, record: Dict[str, Any]) -> str:
        """Format log record as structured JSON"""
        output = {}
        
        if self.include_timestamp:
            output["timestamp"] = record["time"].isoformat()
        
        if self.include_level:
            output["level"] = record["level"].name
        
        # Add standard fields
        output.update({
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
        })
        
        # Add extra fields
        if "extra" in record and record["extra"]:
            output.update(record["extra"])
        
        # Add exception info if present
        if record["exception"]:
            output["exception"] = {
                "type": record["exception"].type.__name__,
                "message": str(record["exception"].value),
                "traceback": record["exception"].traceback
            }
        
        return json.dumps(output, ensure_ascii=False, default=str)


class ColorFormatter:
    """Colorized formatter for console output"""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }
    
    def format(self, record: Dict[str, Any]) -> str:
        """Format log record with colors"""
        level = record["level"].name
        color = self.COLORS.get(level, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
        module = record["name"]
        function = record["function"]
        line = record["line"]
        message = record["message"]
        
        return f"{color}[{timestamp}] {level:8} | {module}:{function}:{line} | {message}{reset}"


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "structured",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = False,
    max_file_size: str = "100MB",
    backup_count: int = 5,
    rotation: str = "1 day",
    compression: str = "gz"
) -> None:
    """Setup enhanced logging system"""
    
    # Remove default logger
    logger.remove()
    
    # Console logging
    if enable_console:
        if log_format == "structured":
            logger.add(
                sys.stdout,
                format=StructuredFormatter().format,
                level=log_level,
                colorize=True,
                backtrace=True,
                diagnose=True
            )
        else:
            logger.add(
                sys.stdout,
                format=ColorFormatter().format,
                level=log_level,
                colorize=True,
                backtrace=True,
                diagnose=True
            )
    
    # File logging
    if enable_file and log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if log_format == "structured" or enable_json:
            # Structured/JSON logging to file
            logger.add(
                log_file,
                format=StructuredFormatter().format,
                level=log_level,
                rotation=rotation,
                retention=f"{backup_count} days",
                compression=compression,
                backtrace=True,
                diagnose=True,
                enqueue=True
            )
        else:
            # Standard logging to file
            logger.add(
                log_file,
                format=LOGURU_FORMAT,
                level=log_level,
                rotation=rotation,
                retention=f"{backup_count} days",
                compression=compression,
                backtrace=True,
                diagnose=True,
                enqueue=True
            )
    
    # Error logging to separate file
    if enable_file and log_file:
        error_log = Path(log_file).parent / "errors.log"
        logger.add(
            str(error_log),
            format=StructuredFormatter().format,
            level="ERROR",
            rotation=rotation,
            retention=f"{backup_count} days",
            compression=compression,
            backtrace=True,
            diagnose=True,
            enqueue=True
        )
    
    # Performance logging
    if enable_file and log_file:
        perf_log = Path(log_file).parent / "performance.log"
        logger.add(
            str(perf_log),
            format=StructuredFormatter().format,
            level="DEBUG",
            filter=lambda record: "performance" in record["extra"].get("tags", []),
            rotation=rotation,
            retention=f"{backup_count} days",
            compression=compression,
            enqueue=True
        )
    
    # Security logging
    if enable_file and log_file:
        security_log = Path(log_file).parent / "security.log"
        logger.add(
            str(security_log),
            format=StructuredFormatter().format,
            level="INFO",
            filter=lambda record: "security" in record["extra"].get("tags", []),
            rotation=rotation,
            retention=f"{backup_count} days",
            compression=compression,
            enqueue=True
        )
    
    # Intercept standard logging
    class InterceptHandler:
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            frame, depth = sys._getframe(6), 6
            while frame and frame.f_code.co_filename == __file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Replace standard logging handlers
    import logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set specific logger levels
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    
    logger.info("Logging system initialized", extra={"tags": ["system", "logging"]})


def get_logger(name: str = None):
    """Get logger instance with context"""
    return logger.bind(name=name)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    logger.info(
        f"Performance: {operation} completed in {duration:.3f}s",
        extra={
            "tags": ["performance"],
            "operation": operation,
            "duration": duration,
            **kwargs
        }
    )


def log_security(event: str, user_id: str = None, ip_address: str = None, **kwargs):
    """Log security events"""
    logger.info(
        f"Security: {event}",
        extra={
            "tags": ["security"],
            "event": event,
            "user_id": user_id,
            "ip_address": ip_address,
            **kwargs
        }
    )


def log_business(operation: str, user_id: str = None, **kwargs):
    """Log business operations"""
    logger.info(
        f"Business: {operation}",
        extra={
            "tags": ["business"],
            "operation": operation,
            "user_id": user_id,
            **kwargs
        }
    )


def log_error(error: Exception, context: str = None, user_id: str = None, **kwargs):
    """Log errors with context"""
    logger.error(
        f"Error in {context}: {str(error)}",
        extra={
            "tags": ["error"],
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user_id": user_id,
            **kwargs
        },
        exception=error
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    ip_address: str = None,
    **kwargs
):
    """Log API request details"""
    level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
    
    logger.log(
        level,
        f"API {method} {path} - {status_code} ({duration:.3f}s)",
        extra={
            "tags": ["api", "request"],
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "user_id": user_id,
            "ip_address": ip_address,
            **kwargs
        }
    )


def log_video_generation(
    video_id: str,
    script_length: int,
    duration: float,
    quality: str,
    user_id: str = None,
    **kwargs
):
    """Log video generation events"""
    logger.info(
        f"Video generated: {video_id}",
        extra={
            "tags": ["video", "generation"],
            "video_id": video_id,
            "script_length": script_length,
            "duration": duration,
            "quality": quality,
            "user_id": user_id,
            **kwargs
        }
    )


# Context manager for timing operations
class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, operation: str, logger_func=log_performance):
        self.operation = operation
        self.logger_func = logger_func
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger_func(self.operation, duration)


# Decorator for timing functions
def time_operation(operation_name: str = None):
    """Decorator to time function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            with Timer(operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Initialize logging when module is imported
if not logger._core.handlers:
    setup_logging()
