package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"quant-dash-backend/internal/handlers"
)

func main() {
	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Initialize router
	router := mux.NewRouter()

	// Initialize handlers
	h := handlers.NewHandlers()

	// Setup routes
	setupRoutes(router, h)

	// Setup CORS middleware
	router.Use(corsMiddleware)

	log.Printf("Server starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, router))
}

func setupRoutes(router *mux.Router, h *handlers.Handlers) {
	// API routes
	api := router.PathPrefix("/api/v1").Subrouter()
	
	// Health check
	api.HandleFunc("/health", h.HealthCheck).Methods("GET")
	
	// Market data routes (to be implemented)
	api.HandleFunc("/market/stocks", h.GetStocks).Methods("GET")
	api.HandleFunc("/market/stocks/{symbol}", h.GetStock).Methods("GET")
	
	// Portfolio routes (to be implemented)
	api.HandleFunc("/portfolio", h.GetPortfolio).Methods("GET")
	
	// Serve static files from frontend (if needed)
	router.PathPrefix("/").Handler(http.FileServer(http.Dir("./web/")))
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Origin, Content-Type, X-Auth-Token")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}
