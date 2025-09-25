"""
Repository pattern implementation for Takeo-ORM
"""

from typing import Type, List, Optional, Any, Dict
from .decorators import get_entity_metadata
from .connection import get_connection
from .types import ValueDict

class Repository:
    """Base repository class for entity operations"""
    
    def __init__(self, entity_class: Type):
        self.entity_class = entity_class
        self.metadata = get_entity_metadata(entity_class)
        if not self.metadata:
            raise ValueError(f"Entity {entity_class.__name__} not registered. Use @Entity decorator.")
        
        self._connection = get_connection()
    
    def save(self, entity: Any) -> None:
        """Save an entity to the database"""
        if not self._connection.is_connected:
            self._connection.connect()
        
        # Register entity metadata with Go core if not already done
        self._ensure_entity_registered()
        
        # Extract values from entity instance
        values = self._extract_entity_values(entity)
        
        # This will be replaced with actual gopy call
        # orm_instance = self._connection.get_orm_instance()
        # orm_instance.CreateEntity(self.entity_class.__name__, values)
        print(f"Saving {self.entity_class.__name__}: {values}")
    
    def find_by_id(self, id: Any) -> Optional[Any]:
        """Find an entity by its primary key"""
        if not self._connection.is_connected:
            self._connection.connect()
        
        self._ensure_entity_registered()
        
        # This will be replaced with actual gopy call
        # orm_instance = self._connection.get_orm_instance()
        # result = orm_instance.FindEntityByID(self.entity_class.__name__, id)
        # return self._map_dict_to_entity(result) if result else None
        
        print(f"Finding {self.entity_class.__name__} with ID: {id}")
        return None
    
    def find_all(self) -> List[Any]:
        """Find all entities of this type"""
        if not self._connection.is_connected:
            self._connection.connect()
        
        self._ensure_entity_registered()
        
        # This will be replaced with actual gopy call
        # orm_instance = self._connection.get_orm_instance()
        # results = orm_instance.FindAllEntities(self.entity_class.__name__)
        # return [self._map_dict_to_entity(result) for result in results]
        
        print(f"Finding all {self.entity_class.__name__} entities")
        return []
    
    def update(self, entity: Any) -> None:
        """Update an existing entity"""
        if not self._connection.is_connected:
            self._connection.connect()
        
        self._ensure_entity_registered()
        
        # Extract primary key value
        pk_field = self._get_primary_key_field()
        if not pk_field:
            raise ValueError("Entity must have a primary key for updates")
        
        pk_value = getattr(entity, pk_field, None)
        if pk_value is None:
            raise ValueError("Primary key value cannot be None for updates")
        
        # Extract values
        values = self._extract_entity_values(entity, exclude_pk=True)
        
        # This will be replaced with actual gopy call
        # orm_instance = self._connection.get_orm_instance()
        # orm_instance.UpdateEntity(self.entity_class.__name__, pk_value, values)
        print(f"Updating {self.entity_class.__name__} ID {pk_value}: {values}")
    
    def delete(self, id: Any) -> None:
        """Delete an entity by its primary key"""
        if not self._connection.is_connected:
            self._connection.connect()
        
        self._ensure_entity_registered()
        
        # This will be replaced with actual gopy call
        # orm_instance = self._connection.get_orm_instance()
        # orm_instance.DeleteEntity(self.entity_class.__name__, id)
        print(f"Deleting {self.entity_class.__name__} with ID: {id}")
    
    def _ensure_entity_registered(self):
        """Ensure entity metadata is registered with the Go core"""
        if not self._connection.is_connected:
            return
        
        # This will be replaced with actual gopy call
        # orm_instance = self._connection.get_orm_instance()
        # orm_instance.RegisterEntityByName(
        #     self.entity_class.__name__,
        #     self.metadata['table_name'],
        #     self.metadata['columns'],
        #     self.metadata['primary_key'],
        #     self.metadata['auto_increment_columns']
        # )
        pass
    
    def _extract_entity_values(self, entity: Any, exclude_pk: bool = False) -> ValueDict:
        """Extract values from an entity instance"""
        values = {}
        
        # Get all attributes that correspond to columns
        for field_name in dir(entity):
            if field_name.startswith('_'):
                continue
            
            value = getattr(entity, field_name, None)
            if callable(value):
                continue
            
            # Map field name to column name
            column_name = field_name.lower()
            
            # Check if this field corresponds to a database column
            if column_name in self.metadata['columns']:
                if exclude_pk and column_name == self.metadata['primary_key']:
                    continue
                values[column_name] = value
        
        return values
    
    def _get_primary_key_field(self) -> Optional[str]:
        """Get the Python field name for the primary key"""
        pk_column = self.metadata['primary_key']
        
        # Look for a field that maps to the primary key column
        for field_name in dir(self.entity_class):
            if field_name.startswith('_'):
                continue
            
            # Check if field name maps to primary key column
            if field_name.lower() == pk_column:
                return field_name
        
        return None
    
    def _map_dict_to_entity(self, data: Dict[str, Any]) -> Any:
        """Map dictionary data to an entity instance"""
        entity = self.entity_class()
        
        for column_name, value in data.items():
            # Find corresponding field name
            for field_name in dir(entity):
                if field_name.startswith('_') or callable(getattr(entity, field_name, None)):
                    continue
                
                if field_name.lower() == column_name:
                    setattr(entity, field_name, value)
                    break
        
        return entity

def repository(entity_class: Type) -> Repository:
    """Create a repository for an entity class"""
    return Repository(entity_class)