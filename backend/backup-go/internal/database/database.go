package database

import (
	"database/sql"
	"fmt"
	"os"

	_ "github.com/lib/pq" // PostgreSQL driver
)

// DB holds the database connection
type DB struct {
	*sql.DB
}

// NewConnection creates a new database connection
func NewConnection() (*DB, error) {
	// Get database configuration from environment variables
	host := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	dbname := os.Getenv("DB_NAME")

	// Set defaults if not provided
	if host == "" {
		host = "localhost"
	}
	if port == "" {
		port = "5432"
	}
	if user == "" {
		user = "postgres"
	}
	if dbname == "" {
		dbname = "quantdash"
	}

	// Build connection string
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Test the connection
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &DB{db}, nil
}

// Close closes the database connection
func (db *DB) Close() error {
	return db.DB.Close()
}

// CreateTables creates the necessary tables (for development)
func (db *DB) CreateTables() error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(50) UNIQUE NOT NULL,
			email VARCHAR(100) UNIQUE NOT NULL,
			created_at TIMESTAMP DEFAULT NOW(),
			updated_at TIMESTAMP DEFAULT NOW()
		)`,
		`CREATE TABLE IF NOT EXISTS stocks (
			id SERIAL PRIMARY KEY,
			symbol VARCHAR(10) UNIQUE NOT NULL,
			name VARCHAR(100) NOT NULL,
			price DECIMAL(10,2),
			change_amount DECIMAL(10,2),
			change_percent DECIMAL(5,2),
			volume BIGINT,
			market_cap VARCHAR(20),
			pe_ratio DECIMAL(8,2),
			updated_at TIMESTAMP DEFAULT NOW()
		)`,
		`CREATE TABLE IF NOT EXISTS portfolios (
			id SERIAL PRIMARY KEY,
			user_id INTEGER REFERENCES users(id),
			total_value DECIMAL(12,2) DEFAULT 0,
			total_gain DECIMAL(12,2) DEFAULT 0,
			created_at TIMESTAMP DEFAULT NOW(),
			updated_at TIMESTAMP DEFAULT NOW()
		)`,
		`CREATE TABLE IF NOT EXISTS positions (
			id SERIAL PRIMARY KEY,
			portfolio_id INTEGER REFERENCES portfolios(id),
			stock_symbol VARCHAR(10) NOT NULL,
			quantity INTEGER NOT NULL,
			average_price DECIMAL(10,2) NOT NULL,
			current_value DECIMAL(12,2),
			total_gain DECIMAL(12,2),
			created_at TIMESTAMP DEFAULT NOW(),
			updated_at TIMESTAMP DEFAULT NOW()
		)`,
		`CREATE TABLE IF NOT EXISTS market_data (
			id SERIAL PRIMARY KEY,
			symbol VARCHAR(10) NOT NULL,
			date DATE NOT NULL,
			open_price DECIMAL(10,2),
			high_price DECIMAL(10,2),
			low_price DECIMAL(10,2),
			close_price DECIMAL(10,2),
			volume BIGINT,
			created_at TIMESTAMP DEFAULT NOW(),
			UNIQUE(symbol, date)
		)`,
	}

	for _, query := range queries {
		if _, err := db.Exec(query); err != nil {
			return fmt.Errorf("failed to create table: %w", err)
		}
	}

	return nil
}
