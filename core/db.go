package core

import (
	"database/sql"
	"fmt"
	"sync"

	_ "github.com/lib/pq"
)

// DatabaseConfig holds database connection configuration
type DatabaseConfig struct {
	Host     string
	Port     int
	User     string
	Password string
	Database string
	SSLMode  string
}

// DB represents the database connection and operations
type DB struct {
	conn            *sql.DB
	config          *DatabaseConfig
	preparedStmts   map[string]*sql.Stmt
	stmtMutex      sync.RWMutex
}

// NewDB creates a new database connection
func NewDB(config *DatabaseConfig) (*DB, error) {
	connStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		config.Host, config.Port, config.User, config.Password, config.Database, config.SSLMode)

	conn, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("failed to open database connection: %w", err)
	}

	if err := conn.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &DB{
		conn:          conn,
		config:        config,
		preparedStmts: make(map[string]*sql.Stmt),
	}, nil
}

// GetOrCreatePreparedStmt gets or creates a prepared statement
func (db *DB) GetOrCreatePreparedStmt(key, query string) (*sql.Stmt, error) {
	db.stmtMutex.RLock()
	stmt, exists := db.preparedStmts[key]
	db.stmtMutex.RUnlock()
	
	if exists && stmt != nil {
		return stmt, nil
	}
	
	db.stmtMutex.Lock()
	defer db.stmtMutex.Unlock()
	
	// Double-check after acquiring write lock
	if stmt, exists := db.preparedStmts[key]; exists && stmt != nil {
		return stmt, nil
	}
	
	// Create new prepared statement
	newStmt, err := db.conn.Prepare(query)
	if err != nil {
		return nil, fmt.Errorf("failed to prepare statement %s: %w", key, err)
	}
	
	db.preparedStmts[key] = newStmt
	return newStmt, nil
}

// Close closes the database connection and all prepared statements
func (db *DB) Close() error {
	db.stmtMutex.Lock()
	defer db.stmtMutex.Unlock()
	
	// Close all prepared statements
	for _, stmt := range db.preparedStmts {
		if stmt != nil {
			stmt.Close()
		}
	}
	db.preparedStmts = nil
	
	return db.conn.Close()
}

// Ping checks if the database connection is alive
func (db *DB) Ping() error {
	return db.conn.Ping()
}