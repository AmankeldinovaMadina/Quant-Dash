package utils

import (
	"encoding/json"
	"net/http"
	"strconv"
)

// JSONResponse sends a JSON response
func JSONResponse(w http.ResponseWriter, data interface{}, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	if data != nil {
		json.NewEncoder(w).Encode(data)
	}
}

// ErrorResponse sends an error response
func ErrorResponse(w http.ResponseWriter, message string, statusCode int) {
	response := map[string]interface{}{
		"error":   true,
		"message": message,
		"status":  statusCode,
	}
	JSONResponse(w, response, statusCode)
}

// ParseIntParam parses an integer parameter from the URL
func ParseIntParam(param string) (int, error) {
	return strconv.Atoi(param)
}

// ParseFloatParam parses a float parameter from the URL
func ParseFloatParam(param string) (float64, error) {
	return strconv.ParseFloat(param, 64)
}

// ValidateRequired checks if required fields are present
func ValidateRequired(fields map[string]string) []string {
	var missing []string

	for field, value := range fields {
		if value == "" {
			missing = append(missing, field)
		}
	}

	return missing
}
