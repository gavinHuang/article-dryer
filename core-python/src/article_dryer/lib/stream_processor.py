import asyncio
from typing import Any, Dict, Optional, Callable, Awaitable
from ..types import OutputData, OutputHandler

class StreamProcessor:
    def __init__(self, output_handler: Optional[OutputHandler] = None):
        self.output_handler = output_handler
        self._queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None
        self._started = False

    async def process_chunk(self, chunk: str) -> None:
        if self.output_handler:
            await self.output_handler({
                'type': 'text',
                'content': chunk
            })

    async def process_error(self, error: str) -> None:
        if self.output_handler:
            await self.output_handler({
                'type': 'error',
                'content': error
            })

    async def start(self):
        if not self._started:
            self._task = asyncio.create_task(self._process_queue())
            self._started = True

    async def stop(self):
        if self._started:
            await self._queue.put(None)  # Sentinel to stop processing
            if self._task:
                await self._task
                self._task = None
            self._started = False

    async def _process_queue(self):
        while True:
            try:
                item = await self._queue.get()
                if item is None:  # Stop sentinel
                    break
                try:
                    if isinstance(item, Exception):
                        await self.process_error(str(item))
                    else:
                        await self.process_chunk(str(item))
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.process_error(f"Stream processing error: {str(e)}")

    async def write(self, data: Any):
        if not self._started:
            await self.start()
        await self._queue.put(data)

    async def write_error(self, error: Exception):
        if not self._started:
            await self.start()
        await self._queue.put(error)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()