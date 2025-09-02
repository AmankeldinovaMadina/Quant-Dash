"""
Test script for Finnhub API integration.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.services.finnhub import FinnhubService
from app.core.config import settings


async def test_finnhub_api():
    """Test Finnhub API integration."""
    print(f"Testing Finnhub API with key: {settings.FINNHUB_API_KEY[:10]}...")

    try:
        # Test basic API connection
        async with FinnhubService() as finnhub:
            print("\n1. Testing Countries API...")
            countries = await finnhub.get_countries()
            print(f"✅ Successfully fetched {len(countries)} countries")

            # Show first few countries
            for country in countries[:5]:
                print(
                    f"   - {country.get('name', 'N/A')} ({country.get('code', 'N/A')})"
                )

            print("\n2. Testing US Stock Symbols...")
            us_symbols = await finnhub.get_stock_symbols("US")
            print(f"✅ Successfully fetched {len(us_symbols)} US symbols")

            # Show first few symbols
            for symbol in us_symbols[:5]:
                print(
                    f"   - {symbol.get('symbol', 'N/A')}: {symbol.get('description', 'N/A')}"
                )

            print("\n3. Testing Stock Quote (AAPL)...")
            quote = await finnhub.get_quote("AAPL")
            print(f"✅ AAPL Quote:")
            print(f"   - Current Price: ${quote.get('c', 'N/A')}")
            print(f"   - Change: {quote.get('d', 'N/A')}")
            print(f"   - Change %: {quote.get('dp', 'N/A')}%")
            print(f"   - High: ${quote.get('h', 'N/A')}")
            print(f"   - Low: ${quote.get('l', 'N/A')}")
            print(f"   - Open: ${quote.get('o', 'N/A')}")
            print(f"   - Previous Close: ${quote.get('pc', 'N/A')}")

    except Exception as e:
        print(f"❌ Error testing Finnhub API: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    print("🚀 Starting Finnhub API Test...")
    success = asyncio.run(test_finnhub_api())

    if success:
        print("\n✅ All tests passed! Finnhub integration is working.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
