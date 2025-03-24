from typing import Any, Dict, Protocol, Optional, List, Awaitable, Callable
from dataclasses import dataclass
from typing_extensions import TypedDict

@dataclass
class ContentData:
    content: str
    metadata: Dict[str, Any]

@dataclass
class OutputData:
    type: str
    content: Any

OutputHandler = Callable[[OutputData], Awaitable[None]]

class Plugin(Protocol):
    name: str
    async def process(self, data: ContentData, output_handler: Optional[OutputHandler] = None) -> ContentData: ...
    def configure(self, options: Dict[str, Any]) -> None: ...

class PluginConfig(TypedDict):
    name: str
    options: Dict[str, Any]

class PipelineConfig(TypedDict):
    plugins: List[PluginConfig]
    globalOptions: Dict[str, Any]
