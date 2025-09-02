"""
Finnhub API service for market data.

This service provides:
1. Country data retrieval
2. Stock price data
3. WebSocket streaming capabilities
4. Rate limiting and error handling

Finnhub API Documentation: https://finnhub.io/docs/api
"""

import asyncio
import json
import logging
from typing import AsyncIterator, Dict, List, Optional, Any
from datetime import datetime

import aiohttp
import websockets
from app.core.config import settings
from app.data.provider_base import MarketProvider

logger = logging.getLogger(__name__)


class FinnhubError(Exception):
    """Custom exception for Finnhub API errors."""

    pass


class FinnhubService(MarketProvider):
    """
    Service for interacting with Finnhub API.

    Provides both REST API and WebSocket functionality for real-time market data.
    """

    BASE_URL = "https://finnhub.io/api/v1"
    WS_URL = "wss://ws.finnhub.io"

    def __init__(self, api_key: str = None):
        """
        Initialize Finnhub service.

        Args:
            api_key: Finnhub API key. If None, will use settings.FINNHUB_API_KEY
        """
        self.api_key = api_key or settings.FINNHUB_API_KEY
        if not self.api_key:
            raise FinnhubError("Finnhub API key is required")

        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connection: Optional[websockets.WebSocketServerProtocol] = None

    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        if self.ws_connection:
            await self.ws_connection.close()

    async def subscribe(self, symbols: List[str]):
        """Subscribe to real-time updates for a list of symbols."""
        if not self.ws_connection:
            await self.connect_websocket()

        for symbol in symbols:
            subscribe_message = {"type": "subscribe", "symbol": symbol}
            try:
                await self.ws_connection.send(json.dumps(subscribe_message))
                logger.info(f"Subscribed to real-time updates for {symbol}")
            except Exception as e:
                logger.error(f"Failed to subscribe to {symbol}: {str(e)}")
                # Continue to next symbol

    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from real-time updates for a list of symbols."""
        if not self.ws_connection:
            logger.warning("No WebSocket connection to unsubscribe from")
            return

        for symbol in symbols:
            unsubscribe_message = {"type": "unsubscribe", "symbol": symbol}
            try:
                await self.ws_connection.send(json.dumps(unsubscribe_message))
                logger.info(f"Unsubscribed from real-time updates for {symbol}")
            except Exception as e:
                logger.error(f"Failed to unsubscribe from {symbol}: {str(e)}")

    async def get_history(self, symbol: str, resolution: str, from_ts: int, to_ts: int) -> List[Dict]:
        """Get historical candle data for a stock."""
        return await self.get_candles(symbol, resolution, from_ts, to_ts)

    async def stream(self) -> AsyncIterator[Dict]:
        """Yields real-time market data messages."""
        if not self.ws_connection:
            await self.connect_websocket()

        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                if data.get("type") == "trade":
                    for trade in data.get("data", []):
                        yield {
                            "type": "tick",
                            "symbol": trade.get("s"),
                            "price": trade.get("p"),
                            "ts": trade.get("t"),
                        }
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed during streaming.")
        except Exception as e:
            logger.error(f"Error during WebSocket streaming: {e}")
            raise FinnhubError(f"WebSocket stream error: {e}")

    async def get_countries(self) -> List[Dict[str, str]]:
        """
        Get list of supported countries.

        Returns:
            List of countries with code and name

        Example response:
        [
            {"code": "US", "name": "United States"},
            {"code": "DE", "name": "Germany"},
            ...
        ]
        """
        try:
            logger.info("Fetching countries from Finnhub API")
            data = await self._make_request("/country")

            if not isinstance(data, list):
                raise FinnhubError("Unexpected response format for countries endpoint")

            logger.info(f"Successfully fetched {len(data)} countries")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch countries: {str(e)}")
            raise FinnhubError(f"Failed to fetch countries: {str(e)}")

    async def get_stock_symbols(self, exchange: str) -> List[Dict[str, Any]]:
        """
        Get stock symbols for a specific exchange.

        Args:
            exchange: Exchange code (e.g., "US", "TO", "L")

        Returns:
            List of stock symbols with metadata
        """
        try:
            logger.info(f"Fetching stock symbols for exchange: {exchange}")
            data = await self._make_request("/stock/symbol", {"exchange": exchange})

            if not isinstance(data, list):
                raise FinnhubError(
                    "Unexpected response format for stock symbols endpoint"
                )

            logger.info(f"Successfully fetched {len(data)} symbols for {exchange}")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch stock symbols for {exchange}: {str(e)}")
            raise FinnhubError(f"Failed to fetch stock symbols: {str(e)}")

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a stock symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL", "TSLA")

        Returns:
            Quote data with current price, change, etc.
        """
        try:
            logger.info(f"Fetching quote for symbol: {symbol}")
            data = await self._make_request("/quote", {"symbol": symbol})

            # Add timestamp for our internal tracking
            data["timestamp"] = datetime.utcnow().isoformat()
            data["symbol"] = symbol

            logger.info(
                f"Successfully fetched quote for {symbol}: ${data.get('c', 'N/A')}"
            )
            return data

        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {str(e)}")
            raise FinnhubError(f"Failed to fetch quote: {str(e)}")

    async def get_candles(
        self, symbol: str, resolution: str, from_timestamp: int, to_timestamp: int
    ) -> Dict[str, Any]:
        """
        Get historical candle data for a stock.

        Args:
            symbol: Stock symbol
            resolution: Resolution (1, 5, 15, 30, 60, D, W, M)
            from_timestamp: Unix timestamp
            to_timestamp: Unix timestamp

        Returns:
            Candle data with OHLCV
        """
        try:
            logger.info(f"Fetching candles for {symbol}, resolution: {resolution}")
            params = {
                "symbol": symbol,
                "resolution": resolution,
                "from": from_timestamp,
                "to": to_timestamp,
            }
            data = await self._make_request("/stock/candle", params)

            if data.get("s") == "no_data":
                logger.warning(f"No candle data available for {symbol}")
                return {"status": "no_data", "symbol": symbol}

            logger.info(
                f"Successfully fetched {len(data.get('c', []))} candles for {symbol}"
            )
            return data

        except Exception as e:
            logger.error(f"Failed to fetch candles for {symbol}: {str(e)}")
            raise FinnhubError(f"Failed to fetch candles: {str(e)}")

    async def connect_websocket(self) -> websockets.WebSocketServerProtocol:
        """
        Connect to Finnhub WebSocket for real-time data.

        Returns:
            WebSocket connection
        """
        try:
            logger.info("Connecting to Finnhub WebSocket")
            uri = f"{self.WS_URL}?token={self.api_key}"
            self.ws_connection = await websockets.connect(uri)
            logger.info("Successfully connected to Finnhub WebSocket")
            return self.ws_connection

        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {str(e)}")
            raise FinnhubError(f"WebSocket connection failed: {str(e)}")

    async def listen_for_updates(self, callback=None):
        """
        Listen for real-time updates from WebSocket.

        Args:
            callback: Optional callback function to handle messages
        """
        if not self.ws_connection:
            raise FinnhubError("WebSocket connection not established")

        try:
            logger.info("Starting to listen for real-time updates")
            async for message in self.ws_connection:
                try:
                    data = json.loads(message)
                    logger.debug(f"Received WebSocket message: {data}")

                    if callback:
                        await callback(data)
                    else:
                        # Default handling - just log
                        if data.get("type") == "trade":
                            trades = data.get("data", [])
                            for trade in trades:
                                symbol = trade.get("s")
                                price = trade.get("p")
                                timestamp = trade.get("t")
                                logger.info(
                                    f"Trade update: {symbol} @ ${price} at {timestamp}"
                                )

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in WebSocket message: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {str(e)}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {str(e)}")
            raise FinnhubError(f"WebSocket listener error: {str(e)}")


# Singleton instance for the application
_finnhub_service: Optional[FinnhubService] = None


async def get_finnhub_service() -> FinnhubService:
    """
    Get or create Finnhub service instance.

    Returns:
        FinnhubService instance
    """
    global _finnhub_service

    if _finnhub_service is None:
        _finnhub_service = FinnhubService()

    return _finnhub_service


async def cleanup_finnhub_service():
    """Clean up Finnhub service resources."""
    global _finnhub_service

    if _finnhub_service:
        if _finnhub_service.session:
            await _finnhub_service.session.close()
        if _finnhub_service.ws_connection:
            await _finnhub_service.ws_connection.close()
        _finnhub_service = None
