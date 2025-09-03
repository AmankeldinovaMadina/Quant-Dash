"""
WebSocket protocol schemas.
"""

from pydantic import BaseModel, Field


class SubscribeMessage(BaseModel):
    type: str = Field(..., pattern="^subscribe$")
    symbol: str


class UnsubscribeMessage(BaseModel):
    type: str = Field(..., pattern="^unsubscribe$")
    symbol: str


class TickMessage(BaseModel):
    type: str = "tick"
    symbol: str
    price: float
    ts: int
