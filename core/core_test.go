package core

import (
	"testing"
)

func TestDatabaseConfig(t *testing.T) {
	config := &DatabaseConfig{
		Host:     "localhost",
		Port:     5432,
		User:     "testuser",
		Password: "testpass",
		Database: "testdb",
		SSLMode:  "disable",
	}

	if config.Host != "localhost" {
		t.Errorf("Expected host 'localhost', got '%s'", config.Host)
	}

	if config.Port != 5432 {
		t.Errorf("Expected port 5432, got %d", config.Port)
	}
}

func TestNewDB(t *testing.T) {
	// Test with invalid config (should fail to connect)
	config := &DatabaseConfig{
		Host:     "invalid-host",
		Port:     5432,
		User:     "testuser",
		Password: "testpass",
		Database: "testdb",
		SSLMode:  "disable",
	}

	_, err := NewDB(config)
	if err == nil {
		t.Error("Expected error when connecting to invalid host")
	}
}

func TestEntityRegistryBasics(t *testing.T) {
	registry := NewEntityRegistry()

	if registry == nil {
		t.Error("Expected registry to be created")
	}

	// Test entity registration and retrieval
	metadata := &EntityMetadata{
		TableName:  "test_table",
		PrimaryKey: "id",
		Columns:    make(map[string]ColumnMetadata),
	}

	registry.entities["TestEntity"] = metadata

	retrieved, exists := registry.GetEntity("TestEntity")
	if !exists {
		t.Error("Expected entity to exist in registry")
	}

	if retrieved.TableName != "test_table" {
		t.Errorf("Expected table name 'test_table', got '%s'", retrieved.TableName)
	}
}