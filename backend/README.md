# Backend - FastAPIPython FastAPI backend for the Quant-Dash quantitative trading dashboard.## Project Structure```backend/├── app/│   ├── api/│   │   └── v1/│   │       └── endpoints/    # API endpoints│   ├── core/                 # Core configuration│   ├── models/               # Pydantic models│   ├── services/             # Business logic│   ├── database/             # Database models and connection│   ├── utils/                # Utility functions│   └── main.py              # FastAPI application├── requirements.txt          # Python dependencies├── start.sh                 # Startup script└── .env.example             # Environment variables example```## Getting Started### Option 1: Using the start script (Recommended)```bash./start.sh```### Option 2: Manual setup1. Create virtual environment:   ```bash   python3 -m venv venv   source venv/bin/activate  # On Windows: venv\Scripts\activate   ```2. Install dependencies:   ```bash   pip install -r requirements.txt   ```3. Copy environment configuration:   ```bash   cp .env.example .env   ```4. Run the server:   ```bash   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload   ```

## API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health
- `GET /health` - Health check
- `GET /api/v1/health` - Detailed health check

### Market Data
- `GET /api/v1/market/stocks` - Get list of stocks
- `GET /api/v1/market/stocks/{symbol}` - Get specific stock data
- `GET /api/v1/market/stocks/{symbol}/history` - Get historical data

### Portfolio
- `GET /api/v1/portfolio` - Get portfolio information
- `GET /api/v1/portfolio/positions` - Get all positions
- `POST /api/v1/portfolio/positions` - Create new position
- `GET /api/v1/portfolio/performance` - Get portfolio performance

## Technologies

- **Framework**: FastAPI (High-performance Python web framework)
- **ASGI Server**: Uvicorn
- **Data Validation**: Pydantic
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Caching**: Redis
- **Authentication**: JWT (Python-JOSE)
- **Background Tasks**: Celery

## Development

### Running with auto-reload
```bash
uvicorn app.main:app --reload
```

### Running tests (when implemented)
```bash
pytest
```

## TODO

- [ ] Implement database models and connections
- [ ] Add authentication and authorization
- [ ] Integrate with market data APIs (Alpha Vantage, IEX Cloud, etc.)
- [ ] Add background tasks for data fetching
- [ ] Implement caching with Redis
- [ ] Add logging configuration
- [ ] Add unit and integration tests
- [ ] Add database migrations with Alembic
- [ ] Add Docker support
- [ ] Add monitoring and metrics
