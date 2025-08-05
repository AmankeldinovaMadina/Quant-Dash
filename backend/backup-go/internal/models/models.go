package models

import "time"

// Stock represents a stock with its basic information
type Stock struct {
	ID            int       `json:"id" db:"id"`
	Symbol        string    `json:"symbol" db:"symbol"`
	Name          string    `json:"name" db:"name"`
	Price         float64   `json:"price" db:"price"`
	Change        float64   `json:"change" db:"change"`
	ChangePercent float64   `json:"change_percent" db:"change_percent"`
	Volume        int64     `json:"volume" db:"volume"`
	MarketCap     string    `json:"market_cap" db:"market_cap"`
	PERatio       float64   `json:"pe_ratio" db:"pe_ratio"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// Portfolio represents a user's portfolio
type Portfolio struct {
	ID         int        `json:"id" db:"id"`
	UserID     int        `json:"user_id" db:"user_id"`
	TotalValue float64    `json:"total_value" db:"total_value"`
	TotalGain  float64    `json:"total_gain" db:"total_gain"`
	CreatedAt  time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt  time.Time  `json:"updated_at" db:"updated_at"`
	Positions  []Position `json:"positions,omitempty"`
}

// Position represents a position in a portfolio
type Position struct {
	ID           int     `json:"id" db:"id"`
	PortfolioID  int     `json:"portfolio_id" db:"portfolio_id"`
	StockSymbol  string  `json:"stock_symbol" db:"stock_symbol"`
	Quantity     int     `json:"quantity" db:"quantity"`
	AveragePrice float64 `json:"average_price" db:"average_price"`
	CurrentValue float64 `json:"current_value" db:"current_value"`
	TotalGain    float64 `json:"total_gain" db:"total_gain"`
}

// User represents a user in the system
type User struct {
	ID        int       `json:"id" db:"id"`
	Username  string    `json:"username" db:"username"`
	Email     string    `json:"email" db:"email"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// MarketData represents historical market data
type MarketData struct {
	ID        int       `json:"id" db:"id"`
	Symbol    string    `json:"symbol" db:"symbol"`
	Date      time.Time `json:"date" db:"date"`
	Open      float64   `json:"open" db:"open"`
	High      float64   `json:"high" db:"high"`
	Low       float64   `json:"low" db:"low"`
	Close     float64   `json:"close" db:"close"`
	Volume    int64     `json:"volume" db:"volume"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}
