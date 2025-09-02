"""
Base classes and protocols for market data providers.
"""
from typing import AsyncIterator, Dict, List, Protocol


class MarketProvider(Protocol):
    """
    Protocol for a market data provider.

    A provider can stream live data and fetch historical data.
    """

    async def subscribe(self, symbols: List[str]):
        """Subscribe to real-time updates for a list of symbols."""
        ...

    async def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from real-time updates for a list of symbols."""
        ...

    async def get_history(self, symbol: str, interval: str, limit: int) -> List[Dict]:
        """Fetch historical data for a symbol."""
        ...

    def stream(self) -> AsyncIterator[Dict]:
        """
        Yields real-time market data messages.

        Example message:
        {"type": "tick", "symbol": "AAPL", "price": 150.0, "ts": 1678886400}
        """
        ...
