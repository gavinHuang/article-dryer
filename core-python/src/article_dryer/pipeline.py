import json
import yaml
import logging
import asyncio
import traceback
from typing import List, Optional, Dict, Any, Union
from .types import Plugin, ContentData, OutputHandler, PipelineConfig
from .plugin_registry import PluginRegistry
from .lib.web_adapter import WebRequest, WebResponse, WebOutputAdapter, WebStreamHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, plugins: List[Plugin] = None, output_handler: Optional[OutputHandler] = None):
        self.plugins = plugins or []
        self.output_handler = output_handler or self.default_output_handler
        self.web_adapter: Optional[WebOutputAdapter] = None

    async def default_output_handler(self, output):
        if self.web_adapter:
            await self.web_adapter.handle_output(output)
        elif output.type == 'error':
            print(f"ERROR: {output.content}", flush=True)
        else:
            print(json.dumps(output.content, indent=2), flush=True)

    @classmethod
    def from_config_file(cls, config_path: str, output_handler: Optional[OutputHandler] = None) -> 'Pipeline':
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return cls.from_config_object(config, output_handler)

    @classmethod
    def from_config_object(cls, config: PipelineConfig, output_handler: Optional[OutputHandler] = None) -> 'Pipeline':
        registry = PluginRegistry.get_instance()
        plugins = []
        
        for plugin_config in config['plugins']:
            merged_config = {
                **config.get('globalOptions', {}),
                **plugin_config.get('options', {})
            }
            plugin = registry.create(plugin_config['name'], merged_config)
            if hasattr(plugin, 'configure'):
                plugin.configure(plugin_config.get('options', {}))
            plugins.append(plugin)
        
        return cls(plugins, output_handler)

    def add_plugin(self, plugin: Plugin) -> 'Pipeline':
        self.plugins.append(plugin)
        return self

    def set_output_handler(self, handler: OutputHandler) -> 'Pipeline':
        self.output_handler = handler
        return self

    def bind_to_web(self, response: WebResponse, stream_handler: Optional[WebStreamHandler] = None) -> 'Pipeline':
        self.web_adapter = WebOutputAdapter(response, stream_handler)
        return self

    async def process_web_request(self, request: WebRequest) -> None:
        if not self.web_adapter:
            raise RuntimeError('Pipeline not bound to web response')

        try:
            content = request.body if isinstance(request.body, str) else json.dumps(request.body)
            result = await self.process(content)
            await self.web_adapter.handle_output(result)
            await self.web_adapter.complete()
        except Exception as err:
            await self.web_adapter.handle_error(err)

    async def process(self, content: str, initial_metadata: Dict[str, Any] = None) -> ContentData:
        data = ContentData(
            content=content,
            metadata=initial_metadata or {}
        )

        for plugin in self.plugins:
            try:
                data = await plugin.process(data, self.output_handler)
            except Exception as err:
                # Print detailed stack trace
                traceback.print_exc()
                logger.error(f"Error processing plugin {plugin.name}: {str(err)}", exc_info=True)
                
                if self.output_handler:
                    await self.output_handler({
                        'type': 'error',
                        'content': f"Error in plugin {plugin.name}: {str(err)}"
                    })
                raise

        return data
