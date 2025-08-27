#!/usr/bin/env python3
"""
MoneyPrinterTurboPro - Main Application Entry Point
The Ultimate AI-Powered Video Generation Platform
"""

import asyncio
import multiprocessing
import os
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_database
from app.core.cache import init_cache
from app.core.plugins import load_plugins
from app.webui.main import create_webui_app


def setup_environment():
    """Setup environment variables and paths"""
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variables
    os.environ.setdefault("MONEYPRINTER_PRO_ENV", "development")
    
    # Create necessary directories
    directories = [
        "logs",
        "cache",
        "temp",
        "output",
        "storage",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import torch
        import moviepy
        import openai
        import anthropic
        logger.info("✅ All core dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Please install all dependencies with: pip install -r requirements.txt")
        return False


def check_gpu():
    """Check GPU availability and setup"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"🚀 GPU detected: {gpu_name} (Count: {gpu_count})")
            
            # Set GPU memory limit
            if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                torch.cuda.set_per_process_memory_fraction(0.8)
                logger.info("GPU memory limit set to 80%")
            
            return True
        else:
            logger.warning("⚠️  No GPU detected, using CPU mode")
            return False
    except ImportError:
        logger.warning("⚠️  PyTorch not available, GPU acceleration disabled")
        return False


async def start_api_server():
    """Start the FastAPI server"""
    from app.api.main import create_app
    
    app = create_app()
    
    config = uvicorn.Config(
        app=app,
        host=settings.app.host,
        port=settings.app.port,
        workers=settings.app.workers,
        reload=settings.app.reload,
        log_level=settings.app.log_level.lower(),
        access_log=True,
        use_colors=True
    )
    
    server = uvicorn.Server(config)
    logger.info(f"🚀 Starting API server on {settings.app.host}:{settings.app.port}")
    await server.serve()


async def start_webui_server():
    """Start the Streamlit WebUI server"""
    import subprocess
    import threading
    
    def run_streamlit():
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "webui/main.py",
            "--server.port", str(settings.app.webui_port),
            "--server.address", settings.app.host,
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Streamlit server failed: {e}")
    
    # Start Streamlit in a separate thread
    thread = threading.Thread(target=run_streamlit, daemon=True)
    thread.start()
    
    logger.info(f"🌐 Starting WebUI server on {settings.app.host}:{settings.app.webui_port}")
    
    # Wait a bit for Streamlit to start
    await asyncio.sleep(3)


async def start_metrics_server():
    """Start the Prometheus metrics server"""
    if not settings.monitoring.prometheus_enabled:
        return
    
    from prometheus_client import start_http_server
    
    try:
        start_http_server(settings.monitoring.prometheus_port)
        logger.info(f"📊 Metrics server started on port {settings.monitoring.prometheus_port}")
    except Exception as e:
        logger.warning(f"Failed to start metrics server: {e}")


async def main_async():
    """Main async function"""
    try:
        # Initialize core components
        logger.info("🔧 Initializing MoneyPrinterTurboPro...")
        
        # Setup logging
        setup_logging()
        
        # Initialize database
        init_database()
        
        # Initialize cache
        init_cache()
        
        # Load plugins
        load_plugins()
        
        # Check GPU
        check_gpu()
        
        # Start servers
        tasks = []
        
        if settings.app.enable_api:
            tasks.append(start_api_server())
        
        if settings.app.enable_webui:
            tasks.append(start_webui_server())
        
        if settings.monitoring.prometheus_enabled:
            tasks.append(start_metrics_server())
        
        if not tasks:
            logger.warning("No servers enabled in configuration")
            return
        
        # Run all servers concurrently
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down MoneyPrinterTurboPro...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


@click.command()
@click.option('--config', '-c', default='config.toml', help='Configuration file path')
@click.option('--api-only', is_flag=True, help='Start only the API server')
@click.option('--webui-only', is_flag=True, help='Start only the WebUI server')
@click.option('--dev', is_flag=True, help='Start in development mode')
@click.option('--port', '-p', type=int, help='Override API server port')
@click.option('--webui-port', '-w', type=int, help='Override WebUI server port')
@click.option('--host', '-h', default='0.0.0.0', help='Override server host')
@click.option('--workers', '-w', type=int, help='Override number of workers')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--log-level', '-l', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Override log level')
def main(config, api_only, webui_only, dev, port, webui_port, host, workers, reload, log_level):
    """MoneyPrinterTurboPro - AI-Powered Video Generation Platform"""
    
    # Setup environment
    setup_environment()
    
    # Load configuration
    os.environ.setdefault("MONEYPRINTER_PRO_CONFIG", config)
    
    # Override settings from command line
    if port:
        os.environ["MONEYPRINTER_PRO_API_PORT"] = str(port)
    if webui_port:
        os.environ["MONEYPRINTER_PRO_WEBUI_PORT"] = str(webui_port)
    if host:
        os.environ["MONEYPRINTER_PRO_HOST"] = host
    if workers:
        os.environ["MONEYPRINTER_PRO_WORKERS"] = str(workers)
    if reload:
        os.environ["MONEYPRINTER_PRO_RELOAD"] = "true"
    if log_level:
        os.environ["MONEYPRINTER_PRO_LOG_LEVEL"] = log_level
    
    # Development mode overrides
    if dev:
        os.environ["MONEYPRINTER_PRO_ENV"] = "development"
        os.environ["MONEYPRINTER_PRO_RELOAD"] = "true"
        os.environ["MONEYPRINTER_PRO_LOG_LEVEL"] = "DEBUG"
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Override server settings based on flags
    if api_only:
        os.environ["MONEYPRINTER_PRO_ENABLE_WEBUI"] = "false"
    if webui_only:
        os.environ["MONEYPRINTER_PRO_ENABLE_API"] = "false"
    
    # Set multiprocessing start method
    if sys.platform.startswith('win'):
        multiprocessing.set_start_method('spawn', force=True)
    
    # Start the application
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown complete")


if __name__ == "__main__":
    main()
