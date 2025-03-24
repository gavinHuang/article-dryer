from typing import Any, Optional, Protocol, Union
from fastapi import Response
from pydantic import BaseModel

class WebRequest(BaseModel):
    body: Union[str, dict]
    headers: dict = {}

class WebResponse(Protocol):
    async def write(self, data: bytes) -> None: ...
    async def end(self) -> None: ...

class WebStreamHandler(Protocol):
    async def handle(self, data: Any) -> None: ...

class WebOutputAdapter:
    def __init__(self, response: WebResponse, stream_handler: Optional[WebStreamHandler] = None):
        self.response = response
        self.stream_handler = stream_handler

    async def handle_output(self, data: Any) -> None:
        if self.stream_handler:
            await self.stream_handler.handle(data)
        else:
            await self.response.write(str(data).encode())

    async def handle_error(self, error: Exception) -> None:
        error_data = {
            'error': str(error),
            'type': error.__class__.__name__
        }
        await self.response.write(str(error_data).encode())
        await self.complete()

    async def complete(self) -> None:
        await self.response.end()
