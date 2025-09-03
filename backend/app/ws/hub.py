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

        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        for symbol in list(self.subscriptions.keys()):
            if websocket in self.subscriptions[symbol]:
                self.subscriptions[symbol].remove(websocket)
                if not self.subscriptions[symbol]:
                    del self.subscriptions[symbol]
                    asyncio.create_task(self.provider.unsubscribe([symbol]))
        logger.info(f"WebSocket connection closed: {websocket.client}")

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

