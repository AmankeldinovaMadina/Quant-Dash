"""
Simple test for Finnhub configuration.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

try:
    from app.core.config import settings

    print(f"✅ Settings loaded successfully")
    print(f"✅ API Key configured: {bool(settings.FINNHUB_API_KEY)}")
    if settings.FINNHUB_API_KEY:
        print(f"✅ API Key starts with: {settings.FINNHUB_API_KEY[:10]}...")

    from app.services.finnhub import FinnhubService

    print(f"✅ FinnhubService imported successfully")

    # Test service initialization
    service = FinnhubService()
    print(f"✅ FinnhubService initialized successfully")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback

    traceback.print_exc()
