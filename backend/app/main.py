from app.api.v1 import api_router
from app.core.config import settings
from app.data.finnhub import FinnhubService
from app.ws.hub import ConnectionManager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(
    title="Quant-Dash API",
    description="A quantitative trading dashboard API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Initialize services and managers
finnhub_provider = FinnhubService()
connection_manager = ConnectionManager(finnhub_provider)

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


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(connection_manager.broadcast_ticks())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.handle_message(websocket, data)
    except Exception as e:
        # Handle client disconnects and other errors
        pass
    finally:
        connection_manager.disconnect(websocket)


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
