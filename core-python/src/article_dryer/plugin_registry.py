from typing import Dict, Type, Any
from .types import Plugin

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
        if name not in self.plugins:
            raise ValueError(f"Plugin {name} not found")
        
        plugin_class = self.plugins[name]
        plugin = plugin_class()
        
        if options and hasattr(plugin, 'configure'):
            plugin.configure(options)
            
        return plugin
