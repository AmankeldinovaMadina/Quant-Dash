import asyncio
from typing import Any, Dict

from app.api.v1 import api_router
from app.core.config import settings
from app.data.finnhub import FinnhubService
from app.ws.hub import ConnectionManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Quant-Dash API",
    description="A quantitative trading dashboard API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Application state
state: Dict[str, Any] = {}


@app.on_event("startup")
async def startup_event():
    """Handles application startup events."""
    finnhub_provider = FinnhubService()
    await finnhub_provider.__aenter__()  # Manually enter the context

    connection_manager = ConnectionManager(finnhub_provider)

    state["finnhub_provider"] = finnhub_provider
    state["connection_manager"] = connection_manager

    asyncio.create_task(connection_manager.broadcast_ticks())
    print("Application startup complete.")


@app.on_event("shutdown")
async def shutdown_event():
    """Handles application shutdown events."""
    if "finnhub_provider" in state:
        await state["finnhub_provider"].__aexit__(None, None, None)
    print("Application shutdown complete.")


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time data."""
    connection_manager = state["connection_manager"]
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        # Client disconnected, which is an expected event.
        pass
    except Exception as e:
        # Log other unexpected errors for debugging.
        print(f"WebSocket error for client {websocket.client}: {e}")
    finally:
        await connection_manager.disconnect(websocket)


@app.get("/")
async def root():
    return {"message": "Welcome to Quant-Dash API"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Quant-Dash Backend API is running",
        "version": "1.0.0",
    }
