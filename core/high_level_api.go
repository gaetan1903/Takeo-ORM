package core

import (
	"database/sql"
	"fmt"
	"strings"
)

// TakeoManager - Interface principale haut niveau pour l'utilisateur
type TakeoManager struct {
	db       *DB
	registry *EntityRegistry
}

// UpdateData structure pour les updates en batch
type UpdateData struct {
	ID      int64                  `json:"id"`
	Updates map[string]interface{} `json:"updates"`
}

// TakeoTransaction - Gestion des transactions
type TakeoTransaction struct {
	tx       *sql.Tx
	manager  *TakeoManager
	finished bool
}

// NewTakeoManager creates a new high-level ORM manager
func NewTakeoManager(host string, port int, user, password, database, sslmode string) (*TakeoManager, error) {
	config := &DatabaseConfig{
		Host:     host,
		Port:     port,
		User:     user,
		Password: password,
		Database: database,
		SSLMode:  sslmode,
	}

	db, err := NewDB(config)
	if err != nil {
		return nil, err
	}

	registry := NewEntityRegistry()

	return &TakeoManager{
		db:       db,
		registry: registry,
	}, nil
}

// RegisterEntity enregistre une nouvelle entité avec ses métadonnées
func (tm *TakeoManager) RegisterEntity(name, tableName string, columns map[string]string, primaryKey string) error {
	metadata := &EntityMetadata{
		TableName:   tableName,
		Columns:     make(map[string]ColumnMetadata),
		PrimaryKey:  primaryKey,
		ColumnOrder: make([]string, 0, len(columns)),
	}

	// Convert string definitions to ColumnMetadata
	for colName, colDef := range columns {
		metadata.Columns[colName] = ColumnMetadata{
			Name:            colName,
			Type:            colDef,
			IsPrimaryKey:    colName == primaryKey,
			IsAutoIncrement: colName == primaryKey, // Assume PK is auto-increment for now
		}
		metadata.ColumnOrder = append(metadata.ColumnOrder, colName)
	}

	// Use direct registration by name for the high-level API
	tm.registry.RegisterEntityByName(name, metadata)
	return nil
}

// Save sauvegarde une entité et retourne son ID
func (tm *TakeoManager) Save(entityType string, entityData map[string]interface{}) (int64, error) {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return 0, fmt.Errorf("entity %s not registered", entityType)
	}

	query := metadata.BuildInsertQuery() + " RETURNING " + metadata.PrimaryKey
	var queryValues []interface{}

	for _, colName := range metadata.ColumnOrder {
		col := metadata.Columns[colName]
		if !col.IsAutoIncrement {
			if val, exists := entityData[colName]; exists {
				queryValues = append(queryValues, val)
			}
		}
	}

	var id int64
	err := tm.db.conn.QueryRow(query, queryValues...).Scan(&id)
	return id, err
}

// SaveBatch sauvegarde plusieurs entités en une transaction et retourne leurs IDs
func (tm *TakeoManager) SaveBatch(entityType string, entitiesData []map[string]interface{}) ([]int64, error) {
	if len(entitiesData) == 0 {
		return nil, nil
	}

	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return nil, fmt.Errorf("entity %s not registered", entityType)
	}

	// Start transaction
	tx, err := tm.db.conn.Begin()
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()

	// Prepare statement with RETURNING clause
	query := metadata.BuildInsertQuery() + " RETURNING " + metadata.PrimaryKey
	stmt, err := tx.Prepare(query)
	if err != nil {
		return nil, err
	}
	defer stmt.Close()

	var ids []int64

	// Execute for each entity
	for _, entityData := range entitiesData {
		var queryValues []interface{}
		for _, colName := range metadata.ColumnOrder {
			col := metadata.Columns[colName]
			if !col.IsAutoIncrement {
				if val, exists := entityData[colName]; exists {
					queryValues = append(queryValues, val)
				}
			}
		}

		var id int64
		if err := stmt.QueryRow(queryValues...).Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}

	if err := tx.Commit(); err != nil {
		return nil, err
	}

	return ids, nil
}

// FindByID trouve une entité par son ID
func (tm *TakeoManager) FindByID(entityType string, id int64) (map[string]interface{}, error) {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return nil, fmt.Errorf("entity %s not registered", entityType)
	}

	query := metadata.BuildSelectQuery() + " WHERE " + metadata.PrimaryKey + " = $1"
	row := tm.db.conn.QueryRow(query, id)

	result := make(map[string]interface{})
	scanDests := make([]interface{}, len(metadata.ColumnOrder))

	for i := range metadata.ColumnOrder {
		var value interface{}
		scanDests[i] = &value
	}

	if err := row.Scan(scanDests...); err != nil {
		return nil, err
	}

	for i, colName := range metadata.ColumnOrder {
		result[colName] = *scanDests[i].(*interface{})
	}

	return result, nil
}

// FindAll trouve toutes les entités d'un type
func (tm *TakeoManager) FindAll(entityType string) ([]map[string]interface{}, error) {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return nil, fmt.Errorf("entity %s not registered", entityType)
	}

	query := metadata.BuildSelectQuery()
	rows, err := tm.db.conn.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []map[string]interface{}

	for rows.Next() {
		result := make(map[string]interface{})
		scanDests := make([]interface{}, len(metadata.ColumnOrder))

		for i := range metadata.ColumnOrder {
			var value interface{}
			scanDests[i] = &value
		}

		if err := rows.Scan(scanDests...); err != nil {
			return nil, err
		}

		for i, colName := range metadata.ColumnOrder {
			result[colName] = *scanDests[i].(*interface{})
		}

		results = append(results, result)
	}

	return results, rows.Err()
}

// FindWhere trouve des entités selon des conditions
func (tm *TakeoManager) FindWhere(entityType string, conditions map[string]interface{}) ([]map[string]interface{}, error) {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return nil, fmt.Errorf("entity %s not registered", entityType)
	}

	query := metadata.BuildSelectQuery() + " WHERE "
	var conditionParts []string
	var queryValues []interface{}
	paramIndex := 1

	for col, val := range conditions {
		conditionParts = append(conditionParts, fmt.Sprintf("%s = $%d", col, paramIndex))
		queryValues = append(queryValues, val)
		paramIndex++
	}

	query += conditionParts[0]
	for i := 1; i < len(conditionParts); i++ {
		query += " AND " + conditionParts[i]
	}

	rows, err := tm.db.conn.Query(query, queryValues...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []map[string]interface{}

	for rows.Next() {
		result := make(map[string]interface{})
		scanDests := make([]interface{}, len(metadata.ColumnOrder))

		for i := range metadata.ColumnOrder {
			var value interface{}
			scanDests[i] = &value
		}

		if err := rows.Scan(scanDests...); err != nil {
			return nil, err
		}

		for i, colName := range metadata.ColumnOrder {
			result[colName] = *scanDests[i].(*interface{})
		}

		results = append(results, result)
	}

	return results, rows.Err()
}

// Update met à jour une entité
func (tm *TakeoManager) Update(entityType string, id int64, updates map[string]interface{}) error {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType)
	}

	// Build dynamic UPDATE query based on fields to update
	var setParts []string
	var queryValues []interface{}
	paramIndex := 1

	// Add only the fields that are being updated
	for colName, value := range updates {
		if col, exists := metadata.Columns[colName]; exists {
			if !col.IsPrimaryKey && !col.IsAutoIncrement {
				setParts = append(setParts, fmt.Sprintf("%s = $%d", colName, paramIndex))
				queryValues = append(queryValues, value)
				paramIndex++
			}
		}
	}

	if len(setParts) == 0 {
		return fmt.Errorf("no valid fields to update")
	}

	// Build the complete query
	query := fmt.Sprintf("UPDATE %s SET %s WHERE %s = $%d",
		metadata.TableName,
		strings.Join(setParts, ", "),
		metadata.PrimaryKey,
		paramIndex)

	// Add primary key value at the end
	queryValues = append(queryValues, id)

	_, err := tm.db.conn.Exec(query, queryValues...)
	return err
}

// UpdateBatch met à jour plusieurs entités en batch
func (tm *TakeoManager) UpdateBatch(entityType string, updates []UpdateData) error {
	if len(updates) == 0 {
		return nil
	}

	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType)
	}

	// Start transaction
	tx, err := tm.db.conn.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Prepare statement
	query := metadata.BuildUpdateQuery()
	stmt, err := tx.Prepare(query)
	if err != nil {
		return err
	}
	defer stmt.Close()

	// Execute for each update
	for _, update := range updates {
		var queryValues []interface{}

		// Add non-primary key values
		for _, colName := range metadata.ColumnOrder {
			col := metadata.Columns[colName]
			if !col.IsPrimaryKey && !col.IsAutoIncrement {
				if val, exists := update.Updates[colName]; exists {
					queryValues = append(queryValues, val)
				}
			}
		}

		// Add primary key value at the end
		queryValues = append(queryValues, update.ID)

		if _, err := stmt.Exec(queryValues...); err != nil {
			return err
		}
	}

	return tx.Commit()
}

// Delete supprime une entité par ID
func (tm *TakeoManager) Delete(entityType string, id int64) error {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType)
	}

	query := metadata.BuildDeleteQuery()
	_, err := tm.db.conn.Exec(query, id)
	return err
}

// DeleteBatch supprime plusieurs entités par ID en batch
func (tm *TakeoManager) DeleteBatch(entityType string, ids []int64) error {
	if len(ids) == 0 {
		return nil
	}

	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType)
	}

	// Start transaction
	tx, err := tm.db.conn.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Prepare statement
	query := metadata.BuildDeleteQuery()
	stmt, err := tx.Prepare(query)
	if err != nil {
		return err
	}
	defer stmt.Close()

	// Execute for each ID
	for _, id := range ids {
		if _, err := stmt.Exec(id); err != nil {
			return err
		}
	}

	return tx.Commit()
}

// DeleteWhere supprime des entités selon des conditions
func (tm *TakeoManager) DeleteWhere(entityType string, conditions map[string]interface{}) (int64, error) {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return 0, fmt.Errorf("entity %s not registered", entityType)
	}

	query := "DELETE FROM " + metadata.TableName + " WHERE "
	var conditionParts []string
	var queryValues []interface{}
	paramIndex := 1

	for col, val := range conditions {
		conditionParts = append(conditionParts, fmt.Sprintf("%s = $%d", col, paramIndex))
		queryValues = append(queryValues, val)
		paramIndex++
	}

	query += conditionParts[0]
	for i := 1; i < len(conditionParts); i++ {
		query += " AND " + conditionParts[i]
	}

	result, err := tm.db.conn.Exec(query, queryValues...)
	if err != nil {
		return 0, err
	}

	rowsAffected, err := result.RowsAffected()
	return rowsAffected, err
}

// CreateTable crée la table pour une entité
func (tm *TakeoManager) CreateTable(entityType string) error {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType)
	}

	query := fmt.Sprintf("CREATE TABLE IF NOT EXISTS %s (", metadata.TableName)
	var columnDefs []string

	for _, colName := range metadata.ColumnOrder {
		col := metadata.Columns[colName]
		columnDefs = append(columnDefs, fmt.Sprintf("%s %s", colName, col.Type))
	}

	query += strings.Join(columnDefs, ", ") + ")"

	_, err := tm.db.conn.Exec(query)
	return err
}

// DropTable supprime la table d'une entité
func (tm *TakeoManager) DropTable(entityType string) error {
	metadata, exists := tm.registry.GetEntity(entityType)
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType)
	}

	query := "DROP TABLE IF EXISTS " + metadata.TableName + " CASCADE"
	_, err := tm.db.conn.Exec(query)
	return err
}

// BeginTransaction commence une nouvelle transaction
func (tm *TakeoManager) BeginTransaction() (*TakeoTransaction, error) {
	tx, err := tm.db.conn.Begin()
	if err != nil {
		return nil, err
	}

	return &TakeoTransaction{
		tx:       tx,
		manager:  tm,
		finished: false,
	}, nil
}

// Save dans une transaction
func (tx *TakeoTransaction) Save(entityType string, entityData map[string]interface{}) (int64, error) {
	if tx.finished {
		return 0, fmt.Errorf("transaction already finished")
	}

	metadata, exists := tx.manager.registry.GetEntity(entityType)
	if !exists {
		return 0, fmt.Errorf("entity %s not registered", entityType)
	}

	query := metadata.BuildInsertQuery() + " RETURNING " + metadata.PrimaryKey
	var queryValues []interface{}

	for _, colName := range metadata.ColumnOrder {
		col := metadata.Columns[colName]
		if !col.IsAutoIncrement {
			if val, exists := entityData[colName]; exists {
				queryValues = append(queryValues, val)
			}
		}
	}

	var id int64
	err := tx.tx.QueryRow(query, queryValues...).Scan(&id)
	return id, err
}

// Commit finalise la transaction
func (tx *TakeoTransaction) Commit() error {
	if tx.finished {
		return fmt.Errorf("transaction already finished")
	}
	tx.finished = true
	return tx.tx.Commit()
}

// Rollback annule la transaction
func (tx *TakeoTransaction) Rollback() error {
	if tx.finished {
		return fmt.Errorf("transaction already finished")
	}
	tx.finished = true
	return tx.tx.Rollback()
}

// Close ferme la connexion
func (tm *TakeoManager) Close() error {
	return tm.db.Close()
}

// Ping vérifie la connectivité
func (tm *TakeoManager) Ping() error {
	return tm.db.Ping()
}