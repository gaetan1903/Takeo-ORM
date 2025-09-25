package core

import (
	"database/sql"
	"fmt"
	"reflect"
	"strings"
)

// Repository provides CRUD operations for entities
type Repository struct {
	db       *DB
	registry *EntityRegistry
}

// NewRepository creates a new repository
func NewRepository(db *DB, registry *EntityRegistry) *Repository {
	return &Repository{
		db:       db,
		registry: registry,
	}
}

// Create inserts a new entity into the database
func (r *Repository) Create(entity interface{}) error {
	entityType := reflect.TypeOf(entity)
	if entityType.Kind() == reflect.Ptr {
		entityType = entityType.Elem()
	}

	metadata, exists := r.registry.GetEntity(entityType.Name())
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType.Name())
	}

	query := metadata.BuildInsertQuery()
	values := r.extractValues(entity, metadata, false) // false = exclude auto-increment fields

	_, err := r.db.conn.Exec(query, values...)
	return err
}

// FindByID finds an entity by its primary key
func (r *Repository) FindByID(entityType reflect.Type, id interface{}, result interface{}) error {
	if entityType.Kind() == reflect.Ptr {
		entityType = entityType.Elem()
	}

	metadata, exists := r.registry.GetEntity(entityType.Name())
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType.Name())
	}

	query := metadata.BuildSelectQuery() + " WHERE " + metadata.PrimaryKey + " = $1"
	
	row := r.db.conn.QueryRow(query, id)
	return r.scanRowToEntity(row, result, metadata)
}

// FindAll retrieves all entities of a given type
func (r *Repository) FindAll(entityType reflect.Type, results interface{}) error {
	if entityType.Kind() == reflect.Ptr {
		entityType = entityType.Elem()
	}

	metadata, exists := r.registry.GetEntity(entityType.Name())
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType.Name())
	}

	query := metadata.BuildSelectQuery()
	
	rows, err := r.db.conn.Query(query)
	if err != nil {
		return err
	}
	defer rows.Close()

	return r.scanRowsToEntities(rows, results, metadata)
}

// Update updates an existing entity in the database
func (r *Repository) Update(entity interface{}) error {
	entityType := reflect.TypeOf(entity)
	if entityType.Kind() == reflect.Ptr {
		entityType = entityType.Elem()
	}

	metadata, exists := r.registry.GetEntity(entityType.Name())
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType.Name())
	}

	query := metadata.BuildUpdateQuery()
	values := r.extractValues(entity, metadata, true) // true = include primary key at the end

	_, err := r.db.conn.Exec(query, values...)
	return err
}

// Delete deletes an entity by its primary key
func (r *Repository) Delete(entityType reflect.Type, id interface{}) error {
	if entityType.Kind() == reflect.Ptr {
		entityType = entityType.Elem()
	}

	metadata, exists := r.registry.GetEntity(entityType.Name())
	if !exists {
		return fmt.Errorf("entity %s not registered", entityType.Name())
	}

	query := metadata.BuildDeleteQuery()
	_, err := r.db.conn.Exec(query, id)
	return err
}

// extractValues extracts field values from an entity based on metadata
func (r *Repository) extractValues(entity interface{}, metadata *EntityMetadata, includePrimaryKey bool) []interface{} {
	var values []interface{}
	
	entityValue := reflect.ValueOf(entity)
	if entityValue.Kind() == reflect.Ptr {
		entityValue = entityValue.Elem()
	}

	entityType := entityValue.Type()

	// First pass: non-primary key, non-auto-increment fields
	for _, colName := range metadata.ColumnOrder {
		col := metadata.Columns[colName]
		if col.IsAutoIncrement {
			continue
		}
		if col.IsPrimaryKey && !includePrimaryKey {
			continue
		}
		if col.IsPrimaryKey && includePrimaryKey {
			continue // Handle primary key separately at the end
		}

		fieldName := r.findFieldNameByColumn(entityType, colName)
		if fieldName != "" {
			fieldValue := entityValue.FieldByName(fieldName)
			if fieldValue.IsValid() {
				values = append(values, fieldValue.Interface())
			}
		}
	}

	// Add primary key at the end if requested (for UPDATE queries)
	if includePrimaryKey && metadata.PrimaryKey != "" {
		fieldName := r.findFieldNameByColumn(entityType, metadata.PrimaryKey)
		if fieldName != "" {
			fieldValue := entityValue.FieldByName(fieldName)
			if fieldValue.IsValid() {
				values = append(values, fieldValue.Interface())
			}
		}
	}

	return values
}

// findFieldNameByColumn finds the struct field name for a given column name
func (r *Repository) findFieldNameByColumn(entityType reflect.Type, columnName string) string {
	for i := 0; i < entityType.NumField(); i++ {
		field := entityType.Field(i)
		if !field.IsExported() {
			continue
		}

		dbTag := field.Tag.Get("db")
		if dbTag == columnName {
			return field.Name
		}
		
		// If no db tag, use lowercase field name
		if dbTag == "" && strings.ToLower(field.Name) == columnName {
			return field.Name
		}
	}
	return ""
}

// scanRowToEntity scans a single row into an entity
func (r *Repository) scanRowToEntity(row *sql.Row, result interface{}, metadata *EntityMetadata) error {
	resultValue := reflect.ValueOf(result)
	if resultValue.Kind() != reflect.Ptr || resultValue.Elem().Kind() != reflect.Struct {
		return fmt.Errorf("result must be a pointer to struct")
	}

	resultValue = resultValue.Elem()
	resultType := resultValue.Type()

	// Prepare scan destinations
	scanDests := make([]interface{}, len(metadata.ColumnOrder))
	for i, colName := range metadata.ColumnOrder {
		fieldName := r.findFieldNameByColumn(resultType, colName)
		if fieldName != "" {
			field := resultValue.FieldByName(fieldName)
			if field.IsValid() && field.CanSet() {
				scanDests[i] = field.Addr().Interface()
			}
		}
	}

	return row.Scan(scanDests...)
}

// scanRowsToEntities scans multiple rows into a slice of entities
func (r *Repository) scanRowsToEntities(rows *sql.Rows, results interface{}, metadata *EntityMetadata) error {
	resultsValue := reflect.ValueOf(results)
	if resultsValue.Kind() != reflect.Ptr || resultsValue.Elem().Kind() != reflect.Slice {
		return fmt.Errorf("results must be a pointer to slice")
	}

	sliceValue := resultsValue.Elem()
	sliceType := sliceValue.Type()
	elemType := sliceType.Elem()

	for rows.Next() {
		// Create new instance
		newElem := reflect.New(elemType).Elem()
		
		// Prepare scan destinations
		scanDests := make([]interface{}, len(metadata.ColumnOrder))
		for i, colName := range metadata.ColumnOrder {
			fieldName := r.findFieldNameByColumn(elemType, colName)
			if fieldName != "" {
				field := newElem.FieldByName(fieldName)
				if field.IsValid() && field.CanSet() {
					scanDests[i] = field.Addr().Interface()
				}
			}
		}

		if err := rows.Scan(scanDests...); err != nil {
			return err
		}

		// Append to slice
		sliceValue.Set(reflect.Append(sliceValue, newElem))
	}

	return rows.Err()
}