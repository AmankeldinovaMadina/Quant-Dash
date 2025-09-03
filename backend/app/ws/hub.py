"""
WebSocket Hub for real-time communication.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set

from app.data.provider_base import MarketProvider
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self, provider: MarketProvider):
        self.provider = provider
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection: {websocket.client}")

    async def disconnect(self, websocket: WebSocket):
        # Remove from active connections
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected: {websocket.client}")

        # Clean up subscriptions for this websocket
        symbols_to_unsubscribe: List[str] = []
        for symbol, sockets in list(self.subscriptions.items()):
            if websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    # no more subscribers for this symbol
                    del self.subscriptions[symbol]
                    symbols_to_unsubscribe.append(symbol)

        if symbols_to_unsubscribe:
            try:
                await self.provider.unsubscribe(symbols_to_unsubscribe)
            except Exception as e:
                logger.exception("Failed to unsubscribe from provider: %s", e)

    async def handle_message(self, websocket: WebSocket, message: str):
        try:
            data = json.loads(message)
            message_type = data.get("type")
            if message_type == "subscribe":
                symbol = data.get("symbol")
                if symbol:
                    await self.subscribe(websocket, symbol)
            elif message_type == "unsubscribe":
                symbol = data.get("symbol")
                if symbol:
                    await self.unsubscribe(websocket, symbol)
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")

    async def subscribe(self, websocket: WebSocket, symbol: str):
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = set()
            await self.provider.subscribe([symbol])
        self.subscriptions[symbol].add(websocket)
        logger.info(f"Subscribed {websocket.client} to {symbol}")

    async def unsubscribe(self, websocket: WebSocket, symbol: str):
        if symbol in self.subscriptions and websocket in self.subscriptions[symbol]:
            self.subscriptions[symbol].remove(websocket)
            if not self.subscriptions[symbol]:
                del self.subscriptions[symbol]
                await self.provider.unsubscribe([symbol])
            logger.info(f"Unsubscribed {websocket.client} from {symbol}")

    async def broadcast_ticks(self):
        """Background task: read ticks from provider.stream() and broadcast to subscribers."""
        logger.info("Starting broadcast_ticks task")
        while True:
            try:
                async for tick in self.provider.stream():
                    # Normalize tick to a dict
                    if hasattr(tick, "dict"):
                        payload = tick.dict()
                    elif isinstance(tick, dict):
                        payload = tick
                    else:
                        payload = {"data": str(tick)}

                    # Determine symbol key
                    symbol = payload.get("symbol") or payload.get("s") or payload.get("ticker")
                    if not symbol:
                        # If no symbol, broadcast to all connections
                        message = json.dumps(payload)
                        for ws in list(self.active_connections):
                            try:
                                await ws.send_text(message)
                            except Exception:
                                await self.disconnect(ws)
                        continue

                    subscribers = list(self.subscriptions.get(symbol, []))
                    if not subscribers:
                        # avoid busy-looping when no subscribers
                        await asyncio.sleep(0.05)
                        continue

                    message = json.dumps(payload)
                    for ws in subscribers:
                        try:
                            await ws.send_text(message)
                        except Exception:
                            # On any send error, remove the websocket
                            await self.disconnect(ws)
            except Exception:
                logger.exception("Error in broadcast_ticks loop, retrying in 1s")
                await asyncio.sleep(1)

