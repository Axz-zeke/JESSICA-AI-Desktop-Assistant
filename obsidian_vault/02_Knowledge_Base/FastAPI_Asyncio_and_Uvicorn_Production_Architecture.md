# FastAPI, Asyncio, and Uvicorn Production Architecture

## Asynchronous Event Loop & Concurrency
FastAPI leverages Starlette and Pydantic on top of the Python `asyncio` event loop.
- **I/O Bound Endpoints (`async def`):** Non-blocking HTTP endpoints that await database queries, network sockets, or file streams without blocking concurrent requests.
- **CPU/GPU Bound Endpoints (`def` or `asyncio.to_thread`):** Heavy tensor generation and neural inference must be dispatched to worker thread pools (`asyncio.to_thread(cortex.generate, ...)`) to avoid freezing the event loop.

## High-Throughput Production Uvicorn Tuning
```bash
uvicorn jessica_server:app   --host 127.0.0.1   --port 8000   --workers 1   --loop uvloop   --http httptools   --no-access-log
```
