"""
Test FastAPI server with Finnhub integration.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting FastAPI server with Finnhub integration...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📋 API documentation at: http://localhost:8000/docs")
    print("🌍 Test endpoints:")
    print("   - GET /api/v1/health")
    print("   - GET /api/v1/market/countries")
    print("   - GET /api/v1/market/symbols/US")
    print("   - GET /api/v1/market/quote/AAPL")
    print("")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
