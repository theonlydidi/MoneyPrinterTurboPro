"""
Plugin system initialization and management for MoneyPrinterTurboPro
"""

import os
import importlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from .config import settings


def load_plugins():
    """Load and initialize all available plugins"""
    try:
        if not settings.plugins.enable_plugins:
            logger.info("⚠️  Plugin system is disabled")
            return True
        
        plugin_dir = Path(settings.plugins.plugin_directory)
        if not plugin_dir.exists():
            logger.info(f"📁 Creating plugin directory: {plugin_dir}")
            plugin_dir.mkdir(parents=True, exist_ok=True)
            return True
        
        loaded_plugins = []
        
        # Load plugins from directory
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
                
            try:
                plugin_name = plugin_file.stem
                plugin_module = importlib.import_module(f"app.plugins.{plugin_name}")
                
                # Check if plugin has required interface
                if hasattr(plugin_module, 'initialize'):
                    plugin_module.initialize()
                    loaded_plugins.append(plugin_name)
                    logger.info(f"✅ Plugin loaded: {plugin_name}")
                else:
                    logger.warning(f"⚠️  Plugin {plugin_name} missing initialize method")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load plugin {plugin_file.name}: {e}")
        
        logger.info(f"✅ Plugins loaded: {len(loaded_plugins)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Plugin loading failed: {e}")
        return False


def get_available_plugins() -> List[str]:
    """Get list of available plugins"""
    try:
        plugin_dir = Path(settings.plugins.plugin_directory)
        if not plugin_dir.exists():
            return []
        
        plugins = []
        for plugin_file in plugin_dir.glob("*.py"):
            if not plugin_file.name.startswith("__"):
                plugins.append(plugin_file.stem)
        
        return plugins
        
    except Exception as e:
        logger.error(f"❌ Failed to get available plugins: {e}")
        return []


def is_plugin_enabled(plugin_name: str) -> bool:
    """Check if a specific plugin is enabled"""
    return plugin_name in settings.plugins.available_plugins


def get_plugin_info(plugin_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific plugin"""
    try:
        plugin_dir = Path(settings.plugins.plugin_directory)
        plugin_file = plugin_dir / f"{plugin_name}.py"
        
        if not plugin_file.exists():
            return None
        
        # Basic plugin info
        info = {
            "name": plugin_name,
            "file_path": str(plugin_file),
            "enabled": is_plugin_enabled(plugin_name),
            "size_bytes": plugin_file.stat().st_size,
            "modified": plugin_file.stat().st_mtime
        }
        
        return info
        
    except Exception as e:
        logger.error(f"❌ Failed to get plugin info for {plugin_name}: {e}")
        return None


def reload_plugins():
    """Reload all plugins"""
    try:
        logger.info("🔄 Reloading plugins...")
        return load_plugins()
    except Exception as e:
        logger.error(f"❌ Plugin reload failed: {e}")
        return False
