package main

import (
	"fmt"
	"log"

	"github.com/gaetan1903/Takeo-ORM/core"
)

func main() {
	// Example usage of the TakeoORM
	orm, err := core.NewTakeoORM(
		"localhost",
		5432,
		"postgres",
		"password",
		"testdb",
		"disable",
	)
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