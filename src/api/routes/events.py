import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/events", tags=["events"])


async def _stream_events() -> AsyncGenerator[str, None]:
    while True:
        yield "event: heartbeat\ndata: {\"status\":\"ok\"}\n\n"
        await asyncio.sleep(2)


@router.get("")
async def stream_events() -> StreamingResponse:
    return StreamingResponse(_stream_events(), media_type="text/event-stream")
