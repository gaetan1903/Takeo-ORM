package core

import (
	"fmt"
	"reflect"
	"strings"
)

// EntityMetadata holds metadata about an entity
type EntityMetadata struct {
	TableName    string
	PrimaryKey   string
	Columns      map[string]ColumnMetadata
	ColumnOrder  []string
}

// ColumnMetadata holds metadata about a column
type ColumnMetadata struct {
	Name         string
	Type         string
	IsPrimaryKey bool
	IsAutoIncrement bool
	IsNullable   bool
	DefaultValue interface{}
}

// EntityRegistry manages entity metadata
type EntityRegistry struct {
	entities map[string]*EntityMetadata
}

// NewEntityRegistry creates a new entity registry
func NewEntityRegistry() *EntityRegistry {
	return &EntityRegistry{
		entities: make(map[string]*EntityMetadata),
	}
}

// RegisterEntity registers an entity with its metadata
func (r *EntityRegistry) RegisterEntity(entityType reflect.Type, tableName string, metadata *EntityMetadata) {
	r.entities[entityType.Name()] = metadata
}

// GetEntity returns entity metadata by type name
func (r *EntityRegistry) GetEntity(typeName string) (*EntityMetadata, bool) {
	entity, exists := r.entities[typeName]
	return entity, exists
}

// ExtractEntityMetadata extracts metadata from a struct using reflection
func ExtractEntityMetadata(entityType reflect.Type, tableName string) *EntityMetadata {
	if tableName == "" {
		tableName = strings.ToLower(entityType.Name())
	}

	metadata := &EntityMetadata{
		TableName:   tableName,
		Columns:     make(map[string]ColumnMetadata),
		ColumnOrder: make([]string, 0),
	}

	for i := 0; i < entityType.NumField(); i++ {
		field := entityType.Field(i)
		
		// Skip unexported fields
		if !field.IsExported() {
			continue
		}

		column := ColumnMetadata{
			Name: strings.ToLower(field.Name),
			Type: field.Type.String(),
		}

		// Parse struct tags
		if dbTag := field.Tag.Get("db"); dbTag != "" {
			column.Name = dbTag
		}

		if field.Tag.Get("primary_key") == "true" {
			column.IsPrimaryKey = true
			metadata.PrimaryKey = column.Name
		}

		if field.Tag.Get("auto_increment") == "true" {
			column.IsAutoIncrement = true
		}

		if field.Tag.Get("nullable") == "true" {
			column.IsNullable = true
		}

		metadata.Columns[column.Name] = column
		metadata.ColumnOrder = append(metadata.ColumnOrder, column.Name)
	}

	return metadata
}

// BuildSelectQuery builds a SELECT query for an entity
func (m *EntityMetadata) BuildSelectQuery() string {
	columns := strings.Join(m.ColumnOrder, ", ")
	return fmt.Sprintf("SELECT %s FROM %s", columns, m.TableName)
}

// BuildInsertQuery builds an INSERT query for an entity
func (m *EntityMetadata) BuildInsertQuery() string {
	var columns []string
	var placeholders []string
	
	i := 1
	for _, colName := range m.ColumnOrder {
		col := m.Columns[colName]
		if !col.IsAutoIncrement {
			columns = append(columns, colName)
			placeholders = append(placeholders, fmt.Sprintf("$%d", i))
			i++
		}
	}
	
	return fmt.Sprintf("INSERT INTO %s (%s) VALUES (%s)",
		m.TableName,
		strings.Join(columns, ", "),
		strings.Join(placeholders, ", "))
}

// BuildUpdateQuery builds an UPDATE query for an entity
func (m *EntityMetadata) BuildUpdateQuery() string {
	var setParts []string
	
	i := 1
	for _, colName := range m.ColumnOrder {
		col := m.Columns[colName]
		if !col.IsPrimaryKey && !col.IsAutoIncrement {
			setParts = append(setParts, fmt.Sprintf("%s = $%d", colName, i))
			i++
		}
	}
	
	return fmt.Sprintf("UPDATE %s SET %s WHERE %s = $%d",
		m.TableName,
		strings.Join(setParts, ", "),
		m.PrimaryKey,
		i)
}

// BuildDeleteQuery builds a DELETE query for an entity
func (m *EntityMetadata) BuildDeleteQuery() string {
	return fmt.Sprintf("DELETE FROM %s WHERE %s = $1", m.TableName, m.PrimaryKey)
}