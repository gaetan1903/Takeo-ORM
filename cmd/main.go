package main

import (
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/gaetan1903/Takeo-ORM/core"
)

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func main() {
	// Get database configuration from environment variables or use defaults
	host := getEnv("DB_HOST", "localhost")
	port := getEnvInt("DB_PORT", 5432)
	user := getEnv("DB_USER", "postgres")
	password := getEnv("DB_PASSWORD", "postgres")
	database := getEnv("DB_NAME", "postgres")
	sslmode := getEnv("DB_SSLMODE", "disable")
	
	fmt.Printf("Connecting to PostgreSQL at %s:%d (database: %s, user: %s)\n", host, port, database, user)
	
	// Example usage of the TakeoORM
	// Note: This requires a running PostgreSQL database
	orm, err := core.NewTakeoORM(host, port, user, password, database, sslmode)
	if err != nil {
		log.Fatalf("Failed to create TakeoORM: %v", err)
	}
	defer orm.Close()

	// Test connection
	if err := orm.Ping(); err != nil {
		log.Fatalf("Failed to ping database: %v", err)
	}

	fmt.Println("TakeoORM connected successfully!")
}