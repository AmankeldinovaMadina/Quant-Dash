from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Stock Models
class StockBase(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    name: str = Field(..., description="Company name")
    price: float = Field(..., description="Current stock price")
    change: float = Field(..., description="Price change")
    change_percent: float = Field(..., description="Percentage change")
    volume: int = Field(..., description="Trading volume")
    market_cap: Optional[str] = Field(None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")


class Stock(StockBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None


# Portfolio Models
class PositionBase(BaseModel):
    stock_symbol: str = Field(..., description="Stock symbol")
    quantity: int = Field(..., description="Number of shares")
    average_price: float = Field(..., description="Average purchase price")


class Position(PositionBase):
    id: int
    portfolio_id: int
    current_value: float = Field(..., description="Current market value")
    total_gain: float = Field(..., description="Total gain/loss")

    class Config:
        from_attributes = True


class PositionCreate(PositionBase):
    portfolio_id: int


class PortfolioBase(BaseModel):
    total_value: float = Field(..., description="Total portfolio value")
    total_gain: float = Field(..., description="Total gain/loss")


class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    positions: List[Position] = []

    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    user_id: int


# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None


# Market Data Models
class MarketDataBase(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    date: datetime = Field(..., description="Trading date")
    open_price: float = Field(..., description="Opening price")
    high_price: float = Field(..., description="Highest price")
    low_price: float = Field(..., description="Lowest price")
    close_price: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")


class MarketData(MarketDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MarketDataCreate(MarketDataBase):
    pass


# Response Models
class HealthResponse(BaseModel):
    status: str = "healthy"
    message: str = "Quant-Dash Backend API is running"
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    detail: Optional[str] = None
