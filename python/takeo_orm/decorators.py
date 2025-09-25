"""
Decorators for defining entities and columns in Takeo-ORM
"""

import inspect
from typing import Any, Dict, Optional, Type, List
from .types import ColumnType, EntityDict

# Global registry to store entity metadata
_entity_registry: Dict[str, EntityDict] = {}

def Entity(table_name: Optional[str] = None):
    """
    Decorator to mark a class as a database entity.
    
    Args:
        table_name: Name of the database table. If None, uses lowercase class name.
    """
    def decorator(cls: Type) -> Type:
        # Use provided table name or default to lowercase class name
        actual_table_name = table_name or cls.__name__.lower()
        
        # Extract column metadata from the class
        columns = {}
        primary_key = None
        auto_increment_columns = []
        
        # Get type annotations
        annotations = getattr(cls, '__annotations__', {})
        
        for attr_name, attr_type in annotations.items():
            if attr_name.startswith('_'):
                continue
                
            # Check if attribute has column metadata
            attr_value = getattr(cls, attr_name, None)
            
            if isinstance(attr_value, ColumnMeta):
                column_name = attr_value.name or attr_name.lower()
                column_type = attr_value.type or _python_type_to_go_type(attr_type)
                
                columns[column_name] = column_type
                
                if attr_value.primary_key:
                    primary_key = column_name
                    
                if attr_value.auto_increment:
                    auto_increment_columns.append(column_name)
            else:
                # Default column mapping
                column_name = attr_name.lower()
                column_type = _python_type_to_go_type(attr_type)
                columns[column_name] = column_type
        
        # Store entity metadata
        entity_metadata = {
            'table_name': actual_table_name,
            'columns': columns,
            'primary_key': primary_key or 'id',
            'auto_increment_columns': auto_increment_columns
        }
        
        _entity_registry[cls.__name__] = entity_metadata
        
        # Store metadata on the class for easy access
        cls._takeo_metadata = entity_metadata
        
        return cls
    
    return decorator

class ColumnMeta:
    """Metadata for a database column"""
    
    def __init__(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        primary_key: bool = False,
        auto_increment: bool = False,
        nullable: bool = True,
        default: Any = None
    ):
        self.name = name
        self.type = type
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.nullable = nullable
        self.default = default

def Column(
    name: Optional[str] = None,
    type: Optional[ColumnType] = None,
    nullable: bool = True,
    default: Any = None
) -> ColumnMeta:
    """
    Define a database column.
    
    Args:
        name: Column name in the database. If None, uses attribute name.
        type: Column type. If None, inferred from Python type annotation.
        nullable: Whether the column can be NULL.
        default: Default value for the column.
    """
    return ColumnMeta(
        name=name,
        type=type.value if type else None,
        nullable=nullable,
        default=default
    )

def PrimaryKey(
    name: Optional[str] = None,
    auto_increment: bool = True,
    type: Optional[ColumnType] = None
) -> ColumnMeta:
    """
    Define a primary key column.
    
    Args:
        name: Column name in the database. If None, uses attribute name.
        auto_increment: Whether the column auto-increments.
        type: Column type. Defaults to INTEGER.
    """
    return ColumnMeta(
        name=name,
        type=(type or ColumnType.INTEGER).value,
        primary_key=True,
        auto_increment=auto_increment,
        nullable=False
    )

def _python_type_to_go_type(python_type: Type) -> str:
    """Convert Python type to Go type string"""
    type_mapping = {
        int: "int",
        str: "string",
        bool: "bool",
        float: "float64",
        bytes: "[]byte",
    }
    
    # Handle typing module types
    origin = getattr(python_type, '__origin__', None)
    if origin is not None:
        if origin is list:
            return "[]interface{}"
        elif origin is dict:
            return "map[string]interface{}"
    
    return type_mapping.get(python_type, "interface{}")

def get_entity_metadata(entity_class: Type) -> Optional[EntityDict]:
    """Get metadata for an entity class"""
    return _entity_registry.get(entity_class.__name__)

def get_all_entities() -> Dict[str, EntityDict]:
    """Get all registered entity metadata"""
    return _entity_registry.copy()