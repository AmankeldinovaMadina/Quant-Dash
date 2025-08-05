package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
)

// Handlers struct to hold all handler methods
type Handlers struct {
	// Add service dependencies here later
}

// NewHandlers creates a new handlers instance
func NewHandlers() *Handlers {
	return &Handlers{}
}

// HealthCheck endpoint
func (h *Handlers) HealthCheck(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":  "healthy",
		"message": "Quant-Dash Backend API is running",
		"version": "1.0.0",
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// GetStocks returns a list of stocks (placeholder)
func (h *Handlers) GetStocks(w http.ResponseWriter, r *http.Request) {
	// Placeholder response
	stocks := []map[string]interface{}{
		{
			"symbol": "AAPL",
			"name":   "Apple Inc.",
			"price":  150.25,
			"change": 2.15,
		},
		{
			"symbol": "GOOGL",
			"name":   "Alphabet Inc.",
			"price":  2750.80,
			"change": -12.45,
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stocks)
}

// GetStock returns information about a specific stock
func (h *Handlers) GetStock(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	symbol := vars["symbol"]

	// Placeholder response
	stock := map[string]interface{}{
		"symbol":     symbol,
		"name":       "Sample Stock",
		"price":      100.50,
		"change":     1.25,
		"volume":     1000000,
		"market_cap": "1B",
		"pe_ratio":   15.5,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stock)
}

// GetPortfolio returns portfolio information (placeholder)
func (h *Handlers) GetPortfolio(w http.ResponseWriter, r *http.Request) {
	portfolio := map[string]interface{}{
		"total_value": 50000.00,
		"total_gain":  5000.00,
		"positions": []map[string]interface{}{
			{
				"symbol":   "AAPL",
				"quantity": 10,
				"value":    1502.50,
			},
			{
				"symbol":   "GOOGL",
				"quantity": 2,
				"value":    5501.60,
			},
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(portfolio)
}
