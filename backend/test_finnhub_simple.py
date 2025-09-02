"""
Simple test for Finnhub API connectivity using requests.
"""

import requests
import json
from app.core.config import settings


def test_finnhub_simple():
    """Simple test using requests library."""
    api_key = settings.FINNHUB_API_KEY
    print(f"Testing with API key: {api_key[:10]}...")

    # Test countries endpoint
    url = f"https://finnhub.io/api/v1/country?token={api_key}"

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            countries = response.json()
            print(f"✅ Successfully fetched {len(countries)} countries")

            # Show first few countries
            for country in countries[:5]:
                print(
                    f"   - {country.get('name', 'N/A')} ({country.get('code', 'N/A')})"
                )

            return True
        else:
            print(f"❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


if __name__ == "__main__":
    test_finnhub_simple()
