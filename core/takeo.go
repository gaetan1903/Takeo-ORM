package core

import (
	"fmt"
	"reflect"
)

// TakeoORM is the main interface exported to Python
type TakeoORM struct {
	db         *DB
	repository *Repository
	registry   *EntityRegistry
}

// NewTakeoORM creates a new TakeoORM instance
func NewTakeoORM(host string, port int, user, password, database, sslmode string) (*TakeoORM, error) {
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
	repository := NewRepository(db, registry)

	return &TakeoORM{
		db:         db,
		repository: repository,
		registry:   registry,
	}, nil
}

// Close closes the database connection
func (orm *TakeoORM) Close() error {
	return orm.db.Close()
}

// Ping checks database connectivity
func (orm *TakeoORM) Ping() error {
	return orm.db.Ping()
}

// RegisterEntityByName registers an entity by providing metadata directly
// This is designed to be called from Python where reflection is limited
func (orm *TakeoORM) RegisterEntityByName(
	typeName string,
	tableName string,
	columns map[string]string,
	primaryKey string,
	autoIncrementColumns []string,
) {
	metadata := &EntityMetadata{
		TableName:   tableName,
		PrimaryKey:  primaryKey,
		Columns:     make(map[string]ColumnMetadata),
		ColumnOrder: make([]string, 0),
	}

	for colName, colType := range columns {
		column := ColumnMetadata{
			Name: colName,
			Type: colType,
		}

		if colName == primaryKey {
			column.IsPrimaryKey = true
		}

		for _, autoCol := range autoIncrementColumns {
			if colName == autoCol {
				column.IsAutoIncrement = true
				break
			}
		}

		metadata.Columns[colName] = column
		metadata.ColumnOrder = append(metadata.ColumnOrder, colName)
	}

	// Create a dummy type for registration
	dummyType := reflect.TypeOf(struct{}{})
	orm.registry.RegisterEntity(dummyType, tableName, metadata)
	orm.registry.entities[typeName] = metadata
}

// CreateEntity creates a new entity record
func (orm *TakeoORM) CreateEntity(typeName string, values map[string]interface{}) error {
	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return fmt.Errorf("entity %s not registered", typeName)
	}

	query := metadata.BuildInsertQuery()
	var queryValues []interface{}

	for _, colName := range metadata.ColumnOrder {
		col := metadata.Columns[colName]
		if !col.IsAutoIncrement {
			if val, exists := values[colName]; exists {
				queryValues = append(queryValues, val)
			}
		}
	}

	_, err := orm.db.conn.Exec(query, queryValues...)
	return err
}

// CreateEntitiesBatch creates multiple entities in a single transaction (batch operation)
func (orm *TakeoORM) CreateEntitiesBatch(typeName string, entitiesData []map[string]interface{}) error {
	if len(entitiesData) == 0 {
		return nil
	}

	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return fmt.Errorf("entity %s not registered", typeName)
	}

	// Start transaction for better performance
	tx, err := orm.db.conn.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Prepare statement for reuse
	query := metadata.BuildInsertQuery()
	stmt, err := tx.Prepare(query)
	if err != nil {
		return err
	}
	defer stmt.Close()

	// Execute for each entity
	for _, values := range entitiesData {
		var queryValues []interface{}
		for _, colName := range metadata.ColumnOrder {
			col := metadata.Columns[colName]
			if !col.IsAutoIncrement {
				if val, exists := values[colName]; exists {
					queryValues = append(queryValues, val)
				}
			}
		}
		
		if _, err := stmt.Exec(queryValues...); err != nil {
			return err
		}
	}

	return tx.Commit()
}

// FindEntityByID finds an entity by its primary key
func (orm *TakeoORM) FindEntityByID(typeName string, id interface{}) (map[string]interface{}, error) {
	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return nil, fmt.Errorf("entity %s not registered", typeName)
	}

	query := metadata.BuildSelectQuery() + " WHERE " + metadata.PrimaryKey + " = $1"
	
	row := orm.db.conn.QueryRow(query, id)
	
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

// FindAllEntities finds all entities of a given type
func (orm *TakeoORM) FindAllEntities(typeName string) ([]map[string]interface{}, error) {
	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return nil, fmt.Errorf("entity %s not registered", typeName)
	}

	query := metadata.BuildSelectQuery()
	
	rows, err := orm.db.conn.Query(query)
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

// UpdateEntity updates an existing entity
func (orm *TakeoORM) UpdateEntity(typeName string, id interface{}, values map[string]interface{}) error {
	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return fmt.Errorf("entity %s not registered", typeName)
	}

	query := metadata.BuildUpdateQuery()
	var queryValues []interface{}

	// Add non-primary key values
	for _, colName := range metadata.ColumnOrder {
		col := metadata.Columns[colName]
		if !col.IsPrimaryKey && !col.IsAutoIncrement {
			if val, exists := values[colName]; exists {
				queryValues = append(queryValues, val)
			}
		}
	}

	// Add primary key value at the end
	queryValues = append(queryValues, id)

	_, err := orm.db.conn.Exec(query, queryValues...)
	return err
}

// DeleteEntity deletes an entity by its primary key
func (orm *TakeoORM) DeleteEntity(typeName string, id interface{}) error {
	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return fmt.Errorf("entity %s not registered", typeName)
	}

	query := metadata.BuildDeleteQuery()
	_, err := orm.db.conn.Exec(query, id)
	return err
}

// DeleteEntitiesBatch deletes multiple entities by their primary keys in a single transaction
func (orm *TakeoORM) DeleteEntitiesBatch(typeName string, ids []interface{}) error {
	if len(ids) == 0 {
		return nil
	}

	metadata, exists := orm.registry.GetEntity(typeName)
	if !exists {
		return fmt.Errorf("entity %s not registered", typeName)
	}

	// Start transaction for better performance
	tx, err := orm.db.conn.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Prepare statement for reuse
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