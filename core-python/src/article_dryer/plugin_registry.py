import logging
import importlib
import traceback
from typing import Dict, Any, Type, Optional

from .types import Plugin

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginRegistry:
    _instance = None
    
    def __init__(self):
        self.plugins: Dict[str, Type[Plugin]] = {}

    @classmethod
    def get_instance(cls) -> 'PluginRegistry':
        if cls._instance is None:
            cls._instance = PluginRegistry()
        return cls._instance

    def register(self, name: str, plugin_class: Type[Plugin]):
        self.plugins[name] = plugin_class

    def create(self, name: str, options: Dict[str, Any] = None) -> Plugin:
        try:
            if name not in self.plugins:
                raise ValueError(f"Plugin {name} not found")
            
            plugin_class = self.plugins[name]
            plugin = plugin_class()
            
            if options and hasattr(plugin, 'configure'):
                plugin.configure(options)
                
            return plugin
        except Exception as e:
            logger.error(f"Error creating plugin {name}: {str(e)}")
            traceback.print_exc()
            raise
