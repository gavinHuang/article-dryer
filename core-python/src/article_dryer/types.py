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

@dataclass
class Document:
    """Represents a document with text and metadata."""
    text: str
    metadata: Dict[str, Any] = None

    def clone(self) -> 'Document':
        """Create a deep copy of the Document object."""
        return Document(text=self.text, metadata=self.metadata.copy() if self.metadata else None)

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

PluginContext = Dict[str, Any]
