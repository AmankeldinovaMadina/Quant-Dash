# Backend - FastAPI

Python FastAPI backend for the Quant-Dash quantitative trading dashboard.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/    # API endpoints
│   ├── core/                 # Core configuration
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   ├── database/             # Database models and connection
│   ├── utils/                # Utility functions
│   └── main.py              # FastAPI application
├── requirements.txt          # Python dependencies
├── start.sh                 # Startup script
├── venv/                    # Python virtual environment
└── .env.example             # Environment variables example
```

## Getting Started

### Prerequisites
- Python 3.8+ installed on your system
- pip (Python package installer)

### Virtual Environment Setup

This project uses a Python virtual environment to manage dependencies and isolate the project environment. The virtual environment is already included in the repository as `venv/`.

#### Using the existing virtual environment (Recommended)
```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python

# Install/update dependencies if needed
pip install -r requirements.txt
```

#### Creating a new virtual environment (if needed)
```bash
# Create a new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Deactivating the virtual environment
```bash
deactivate
```

### Option 1: Using the start script (Recommended)
```bash
./start.sh
```

### Option 2: Manual setup
1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy environment configuration**:
   ```bash
   cp .env.example .env
   ```

4. **Run the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

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
# Make sure virtual environment is activated first
source venv/bin/activate

# Then run the server
uvicorn app.main:app --reload
```

### Running tests
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the authentication test script
python test_auth.py

# Run pytest tests (when implemented)
pytest
```

### Virtual Environment Management

#### Installing new packages
```bash
# Activate environment
source venv/bin/activate

# Install package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

#### Updating dependencies
```bash
# Activate environment
source venv/bin/activate

# Update all packages
pip install -r requirements.txt --upgrade

# Or update specific package
pip install --upgrade package_name
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
