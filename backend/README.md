# BackendGo backend for the Quant-Dash quantitative trading dashboard.## Project Structure```backend/├── cmd/server/          # Application entry point├── internal/│   ├── handlers/        # HTTP handlers
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   └── database/        # Database connection and queries
├── pkg/
│   └── utils/          # Utility functions
├── go.mod              # Go module definition
└── .env.example        # Environment variables example
```

## Getting Started

1. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   go mod tidy
   ```

3. Run the server:
   ```bash
   go run cmd/server/main.go
   ```

## API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/market/stocks` - Get list of stocks
- `GET /api/v1/market/stocks/{symbol}` - Get specific stock data
- `GET /api/v1/portfolio` - Get portfolio information

## Technologies

- **Framework**: Gorilla Mux for HTTP routing
- **Database**: PostgreSQL (with lib/pq driver)
- **Architecture**: Clean architecture with handlers, services, and models

## TODO

- [ ] Implement database connections
- [ ] Add authentication middleware
- [ ] Integrate with market data APIs
- [ ] Add logging
- [ ] Add configuration management
- [ ] Add unit tests
- [ ] Add API documentation (Swagger)
- [ ] Add Docker support
