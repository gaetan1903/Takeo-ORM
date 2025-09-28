"""
Repository pattern implementation for Takeo-ORM
"""

from typing import Type, List, Optional, Any, Dict
from .decorators import get_entity_metadata
from .connection import get_connection, Connection
from .types import ValueDict


class Repository:
    """Base repository class for entity operations"""

    def __init__(self, entity_class: Type, connection: Optional[Connection] = None):
        self.entity_class = entity_class
        self.metadata = get_entity_metadata(entity_class)
        if not self.metadata:
            raise ValueError(
                f"Entity {entity_class.__name__} not registered. Use @Entity decorator."
            )

        # Utilise la connexion spécifiée ou la connexion par défaut
        self._connection = connection or get_connection()

    def save(self, entity: Any) -> None:
        """Save an entity to the database"""
        if not self._connection.is_connected:
            self._connection.connect()

        # Register entity metadata with Go core if not already done
        self._ensure_entity_registered()

        # Extract values from entity instance
        values = self._extract_entity_values(entity)

        try:
            # Use Go binding
            orm_instance = self._connection.get_orm_instance()
            orm_instance.CreateEntity(self.entity_class.__name__, values)
        except Exception as e:
            raise RuntimeError(f"Failed to save entity: {e}")

    def find_by_id(self, id: Any) -> Optional[Any]:
        """Find an entity by its primary key"""
        if not self._connection.is_connected:
            self._connection.connect()

        self._ensure_entity_registered()

        try:
            # Use Go binding - Convert ID to string
            orm_instance = self._connection.get_orm_instance()
            result = orm_instance.FindEntityByID(self.entity_class.__name__, str(id))
            return self._map_dict_to_entity(result) if result else None
        except Exception as e:
            raise RuntimeError(f"Failed to find entity: {e}")

    def find_all(self) -> List[Any]:
        """Find all entities of this type"""
        if not self._connection.is_connected:
            self._connection.connect()

        self._ensure_entity_registered()

        try:
            # Use Go binding
            orm_instance = self._connection.get_orm_instance()
            results = orm_instance.FindAllEntities(self.entity_class.__name__)
            return [self._map_dict_to_entity(result) for result in results]
        except Exception as e:
            raise RuntimeError(f"Failed to find entities: {e}")

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

        try:
            # Use Go binding - Convert primary key to string
            orm_instance = self._connection.get_orm_instance()
            orm_instance.UpdateEntity(self.entity_class.__name__, str(pk_value), values)
        except Exception as e:
            raise RuntimeError(f"Failed to update entity: {e}")

    def delete(self, id: Any) -> None:
        """Delete an entity by its primary key"""
        if not self._connection.is_connected:
            self._connection.connect()

        self._ensure_entity_registered()

        try:
            # Use Go binding - Convert ID to string
            orm_instance = self._connection.get_orm_instance()
            orm_instance.DeleteEntity(self.entity_class.__name__, str(id))
        except Exception as e:
            raise RuntimeError(f"Failed to delete entity: {e}")

    def _ensure_entity_registered(self):
        """Ensure entity metadata is registered with the Go core"""
        if not self._connection.is_connected:
            return

        try:
            # Import Go types here to avoid circular imports
            import sys
            from pathlib import Path

            # Add bindings to path if not already there
            repo_root = Path(__file__).parent.parent.parent
            bindings_dir = repo_root / "python" / "bindings"
            if str(bindings_dir) not in sys.path:
                sys.path.insert(0, str(bindings_dir))

            from bindings.core import Map_string_string  # ← Corrigé !
            from bindings.go import Slice_string

            # Convertir les métadonnées en Map_string_string (nom_colonne -> type_string)
            columns_dict = {}
            for col_name, col_info in self.metadata["columns"].items():
                # Extraire le type sous forme de chaîne
                if isinstance(col_info, str):
                    # Déjà une chaîne
                    columns_dict[col_name] = col_info
                else:
                    # Objet ColumnMeta - extraire le type ou utiliser str()
                    col_type = getattr(col_info, "type", None)
                    if col_type:
                        columns_dict[col_name] = col_type
                    else:
                        # Fallback - convertir en string
                        columns_dict[col_name] = str(col_info)

            go_columns = Map_string_string(columns_dict)
            go_auto_increment = Slice_string(self.metadata["auto_increment_columns"])

            # Use Go binding
            orm_instance = self._connection.get_orm_instance()
            orm_instance.RegisterEntityByName(
                self.entity_class.__name__,  # str
                self.metadata["table_name"],  # str
                go_columns,  # object with handle
                self.metadata["primary_key"],  # str
                go_auto_increment,  # []str with handle
            )

        except Exception as e:
            # Log but don't fail on registration errors
            pass

    def _extract_entity_values(self, entity: Any, exclude_pk: bool = False):
        """Extract values from an entity instance and convert to Go object"""
        # Import Go types
        import sys
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        bindings_dir = repo_root / "python" / "bindings"
        if str(bindings_dir) not in sys.path:
            sys.path.insert(0, str(bindings_dir))

        from bindings.core import Map_string_interface_

        values = {}

        # Get all attributes that correspond to columns
        for field_name in dir(entity):
            if field_name.startswith("_"):
                continue

            value = getattr(entity, field_name, None)
            if callable(value):
                continue

            # Map field name to column name
            column_name = field_name.lower()

            # Check if this field corresponds to a database column
            if column_name in self.metadata["columns"]:
                if exclude_pk and column_name == self.metadata["primary_key"]:
                    continue

                # Skip ColumnMeta objects - they are class-level metadata, not instance values
                from .decorators import ColumnMeta

                if isinstance(value, ColumnMeta):
                    continue

                # Convert values appropriately for Go compatibility
                if value is None:
                    values[column_name] = None
                else:
                    # Convert all values to strings for Go Map_string_interface_ compatibility
                    str_value = str(value)
                    values[column_name] = str_value

        # Convert to Go Map_string_interface_
        return Map_string_interface_(values)

    def _get_primary_key_field(self) -> Optional[str]:
        """Get the Python field name for the primary key"""
        pk_column = self.metadata["primary_key"]

        # Look for a field that maps to the primary key column
        for field_name in dir(self.entity_class):
            if field_name.startswith("_"):
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
                if field_name.startswith("_") or callable(
                    getattr(entity, field_name, None)
                ):
                    continue

                if field_name.lower() == column_name:
                    # Convert Go values back to appropriate Python types
                    converted_value = self._convert_from_go_value(column_name, value)
                    setattr(entity, field_name, converted_value)
                    break

        return entity

    def _convert_from_go_value(self, column_name: str, value: Any) -> Any:
        """Convert Go values back to appropriate Python types"""
        if value is None:
            return None

        # Check the expected column type from metadata
        column_type = self.metadata["columns"].get(column_name, "string")

        # Handle string representations from Go (like "%!s(int64=25)")
        if isinstance(value, str):
            if value.startswith("%!s(int64=") and value.endswith(")"):
                # Extract number from "%!s(int64=25)"
                try:
                    return int(value.split("=")[1].rstrip(")"))
                except (IndexError, ValueError):
                    pass
            elif column_type == "int":
                try:
                    return int(value)
                except ValueError:
                    pass

        # Convert based on column type
        if column_type == "int":
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        elif column_type == "string":
            return str(value)
        else:
            return value


def repository(
    entity_class: Type, connection: Optional[Connection] = None
) -> Repository:
    """Create a repository for an entity class"""
    return Repository(entity_class, connection)
