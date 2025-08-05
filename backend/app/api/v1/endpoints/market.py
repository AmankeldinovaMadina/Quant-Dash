from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import Stock

router = APIRouter()


@router.get("/stocks", response_model=List[Stock])
async def get_stocks():
    """
    Get a list of all stocks with current market data
    """
    # Placeholder data - replace with actual market data service
    stocks = [
        Stock(
            id=1,
            symbol="AAPL",
            name="Apple Inc.",
            price=150.25,
            change=2.15,
            change_percent=1.45,
            volume=50000000,
            market_cap="2.4T",
            pe_ratio=28.5,
            updated_at="2025-08-05T10:30:00"
        ),
        Stock(
            id=2,
            symbol="GOOGL",
            name="Alphabet Inc.",
            price=2750.80,
            change=-12.45,
            change_percent=-0.45,
            volume=1200000,
            market_cap="1.8T",
            pe_ratio=25.2,
            updated_at="2025-08-05T10:30:00"
        ),
        Stock(
            id=3,
            symbol="MSFT",
            name="Microsoft Corporation",
            price=310.50,
            change=5.25,
            change_percent=1.72,
            volume=25000000,
            market_cap="2.3T",
            pe_ratio=32.1,
            updated_at="2025-08-05T10:30:00"
        )
    ]
    return stocks


@router.get("/stocks/{symbol}", response_model=Stock)
async def get_stock(
    symbol: str = Path(..., description="Stock symbol (e.g., AAPL)")
):
    """
    Get detailed information about a specific stock
    """
    # Placeholder data - replace with actual market data service
    stock_data = {
        "AAPL": Stock(
            id=1,
            symbol="AAPL",
            name="Apple Inc.",
            price=150.25,
            change=2.15,
            change_percent=1.45,
            volume=50000000,
            market_cap="2.4T",
            pe_ratio=28.5,
            updated_at="2025-08-05T10:30:00"
        ),
        "GOOGL": Stock(
            id=2,
            symbol="GOOGL",
            name="Alphabet Inc.",
            price=2750.80,
            change=-12.45,
            change_percent=-0.45,
            volume=1200000,
            market_cap="1.8T",
            pe_ratio=25.2,
            updated_at="2025-08-05T10:30:00"
        )
    }
    
    if symbol.upper() not in stock_data:
        raise HTTPException(status_code=404, detail=f"Stock with symbol '{symbol}' not found")
    
    return stock_data[symbol.upper()]


@router.get("/stocks/{symbol}/history")
async def get_stock_history(
    symbol: str = Path(..., description="Stock symbol"),
    days: int = 30
):
    """
    Get historical market data for a stock
    """
    # Placeholder endpoint - implement with actual market data
    return {
        "symbol": symbol.upper(),
        "days": days,
        "message": "Historical data endpoint - to be implemented"
    }
