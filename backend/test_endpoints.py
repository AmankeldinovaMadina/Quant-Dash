"""
Test HTTP endpoints using httpx client.
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_endpoints():
    """Test all the API endpoints."""

    print("🧪 Testing FastAPI endpoints...")

    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("\n1. Testing Health endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")

            # Test countries endpoint
            print("\n2. Testing Countries endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/market/countries")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Countries found: {len(data)}")
                if data:
                    print(f"   First country: {data[0]}")

            # Test US symbols endpoint
            print("\n3. Testing US Symbols endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/market/symbols/US")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Symbols found: {len(data)}")
                if data:
                    print(f"   First symbol: {data[0]}")

            # Test AAPL quote endpoint
            print("\n4. Testing AAPL Quote endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/market/quote/AAPL")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   AAPL Quote: {data}")

        except httpx.ConnectError:
            print(
                "❌ Cannot connect to server. Make sure the FastAPI server is running:"
            )
            print("   python run_server.py")
        except Exception as e:
            print(f"❌ Error testing endpoints: {str(e)}")


if __name__ == "__main__":
    print("🌐 Testing HTTP endpoints...")
    print("Make sure the FastAPI server is running first!")
    asyncio.run(test_endpoints())
