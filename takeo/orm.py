"""
Takeo-ORM - TypeORM-like API for Python
High-performance ORM with Go backend and TypeORM-inspired syntax
"""

try:
    import orjson

    # Optimize: avoid decode() when possible, work with bytes directly when Go API accepts it
    def json_dumps(obj):
        # Return bytes directly - Go can handle bytes
        result = orjson.dumps(obj)
        # Only decode if we need string (for now, keep compatibility)
        return result.decode("utf-8")

    def json_loads(s):
        # Handle both bytes and str input
        if isinstance(s, str):
            s = s.encode("utf-8")
        return orjson.loads(s)

except ImportError:
    import json

    def json_dumps(obj):
        return json.dumps(obj)

    def json_loads(s):
        return json.loads(s)


from typing import Dict, List, Any, Optional, Type
from .core import core


# Métadonnées de colonnes
class ColumnMeta:
    def __init__(
        self,
        type_def: str,
        primary: bool = False,
        nullable: bool = True,
        unique: bool = False,
        **options,
    ):
        self.type = type_def
        self.primary = primary
        self.nullable = nullable
        self.unique = unique

        # Construire le type SQL complet
        sql_type = type_def
        if not nullable:
            sql_type += " NOT NULL"
        if unique:
            sql_type += " UNIQUE"
        if "default" in options:
            sql_type += f" DEFAULT {options['default']}"

        self.sql_type = sql_type


# Décorateurs TypeORM-style
def Entity(table_name: str):
    """Décorateur @Entity pour marquer une classe comme entité"""

    def decorator(cls):
        cls._takeo_table_name = table_name
        cls._takeo_columns = {}
        cls._takeo_primary_key = None

        # Extraire les métadonnées des colonnes
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, ColumnMeta):
                cls._takeo_columns[attr_name] = {
                    "name": attr_name,
                    "type": attr_value.sql_type,
                    "primary": attr_value.primary,
                    "nullable": attr_value.nullable,
                    "unique": attr_value.unique,
                }
                if attr_value.primary:
                    cls._takeo_primary_key = attr_name

        return cls

    return decorator


def PrimaryGeneratedColumn(type_def: str = "SERIAL PRIMARY KEY"):
    """Décorateur @PrimaryGeneratedColumn pour clé primaire auto-générée"""
    return ColumnMeta(type_def, primary=True)


def Column(
    type_def: str = "VARCHAR(255)",
    nullable: bool = True,
    unique: bool = False,
    **options,
):
    """Décorateur @Column pour colonnes standard"""
    return ColumnMeta(type_def, nullable=nullable, unique=unique, **options)


class TakeoPyTypeORM:
    """Connexion principale TypeORM-style"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        sslmode: str = "disable",
    ):
        self._api = core.NewTakeoAPI(host, port, user, password, database, sslmode)
        self._repositories = {}

    def getRepository(self, entity_class: Type) -> "Repository":
        """Obtient le repository pour une entité (style TypeORM)"""
        class_name = entity_class.__name__

        if class_name not in self._repositories:
            self._register_entity_if_needed(entity_class)
            self._repositories[class_name] = Repository(entity_class, self._api)

        return self._repositories[class_name]

    def _register_entity_if_needed(self, entity_class: Type):
        """Enregistre une entité dans l'API Go"""
        if not hasattr(entity_class, "_takeo_registered"):
            # Préparer les colonnes pour l'API Go
            columns_dict = {}
            for attr_name, col_meta in entity_class._takeo_columns.items():
                columns_dict[col_meta["name"]] = col_meta["type"]

            # Enregistrer dans l'API Go
            columns_json = json_dumps(columns_dict)
            self._api.RegisterEntity(
                entity_class.__name__,
                entity_class._takeo_table_name,
                columns_json,
                entity_class._takeo_primary_key or "id",
            )

            entity_class._takeo_registered = True

    def close(self):
        """Ferme la connexion"""
        self._api.Close()


class Repository:
    """Repository TypeORM-style pour opérations CRUD"""

    def __init__(self, entity_class: Type, api):
        self.entity_class = entity_class
        self._api = api

    def save(self, entity) -> Any:
        """Sauvegarde une entité (style TypeORM)"""
        entity_data = self._entity_to_dict(entity)
        entity_json = json_dumps(entity_data)

        save_result = self._api.Save(self.entity_class.__name__, entity_json)
        if isinstance(save_result, tuple):
            result, error = save_result
            if error:
                raise Exception(f"Save error: {error}")
            # Mettre à jour l'ID de l'entité
            if hasattr(entity, self.entity_class._takeo_primary_key):
                setattr(entity, self.entity_class._takeo_primary_key, result)
            return entity
        else:
            if hasattr(entity, self.entity_class._takeo_primary_key):
                setattr(entity, self.entity_class._takeo_primary_key, save_result)
            return entity

    def saveBatch(self, entities: List[Any]) -> List[Any]:
        """Sauvegarde multiple entités en une seule transaction - OPTIMISÉ"""
        if not entities:
            return []

        # Convert all entities to dicts in one go
        entities_data = []
        for entity in entities:
            entity_data = self._entity_to_dict(entity)
            entities_data.append(entity_data)

        # Single JSON serialization for all entities
        batch_json = json_dumps(entities_data)

        # Single API call instead of N calls
        try:
            # Use SaveBatch if available, otherwise fallback to individual saves
            if hasattr(self._api, "SaveBatch"):
                batch_result = self._api.SaveBatch(
                    self.entity_class.__name__, batch_json
                )
                # Parse batch results and update entity IDs
                if isinstance(batch_result, str):
                    ids = json_loads(batch_result)
                    for i, entity_id in enumerate(ids):
                        if i < len(entities) and hasattr(
                            entities[i], self.entity_class._takeo_primary_key
                        ):
                            setattr(
                                entities[i],
                                self.entity_class._takeo_primary_key,
                                entity_id,
                            )
            else:
                # Fallback to individual saves (still faster due to optimized conversions)
                for entity in entities:
                    self.save(entity)
        except Exception as e:
            # Fallback to individual saves on error
            for entity in entities:
                self.save(entity)

        return entities

    def findOne(self, id: int) -> Optional[Any]:
        """Trouve une entité par ID (style TypeORM)"""
        result = self._api.FindByID(self.entity_class.__name__, id)

        # Gestion flexible du résultat (tuple ou string directe)
        if isinstance(result, tuple):
            json_str, error = result
            if error:
                raise Exception(f"FindOne error: {error}")
            json_to_parse = json_str
        else:
            # Résultat direct en string JSON
            json_to_parse = result

        if json_to_parse:
            try:
                data = json_loads(json_to_parse)
                return self._dict_to_entity(data)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON decode error: {e}")
        return None

    def find(self) -> List[Any]:
        """Trouve toutes les entités (style TypeORM)"""
        result = self._api.FindAll(self.entity_class.__name__)

        # Gestion flexible du résultat (tuple ou string directe)
        if isinstance(result, tuple):
            json_str, error = result
            if error:
                raise Exception(f"Find error: {error}")
            json_to_parse = json_str
        else:
            # Résultat direct en string JSON
            json_to_parse = result

        if json_to_parse:
            try:
                data = json_loads(json_to_parse)
                if isinstance(data, list):
                    return [self._dict_to_entity(item) for item in data]
            except json.JSONDecodeError as e:
                raise Exception(f"JSON decode error: {e}")
        return []

    def update(self, id: int, update_data: Dict[str, Any]):
        """Met à jour une entité (style TypeORM)"""
        update_json = json_dumps(update_data)
        result = self._api.Update(self.entity_class.__name__, id, update_json)
        if result:
            raise Exception(f"Update error: {result}")

    def delete(self, id: int):
        """Supprime une entité (style TypeORM)"""
        result = self._api.Delete(self.entity_class.__name__, id)
        if result:
            raise Exception(f"Delete error: {result}")

    def _entity_to_dict(self, entity) -> Dict[str, Any]:
        """Convertit une entité en dictionnaire - optimisé"""
        # Cache column mapping for better performance
        if not hasattr(self, "_column_mapping"):
            self._column_mapping = {
                attr_name: col_meta["name"]
                for attr_name, col_meta in self.entity_class._takeo_columns.items()
            }

        # Fast dict comprehension instead of loop
        return {
            self._column_mapping[attr_name]: getattr(entity, attr_name)
            for attr_name in self._column_mapping
            if hasattr(entity, attr_name) and getattr(entity, attr_name) is not None
        }

    def _dict_to_entity(self, data: Dict[str, Any]):
        """Convertit un dictionnaire en entité - optimisé"""
        # Cache reverse column mapping
        if not hasattr(self, "_reverse_column_mapping"):
            self._reverse_column_mapping = {
                col_meta["name"]: attr_name
                for attr_name, col_meta in self.entity_class._takeo_columns.items()
            }

        entity = self.entity_class()
        # Fast batch setattr
        for column_name, value in data.items():
            if column_name in self._reverse_column_mapping:
                setattr(entity, self._reverse_column_mapping[column_name], value)
        return entity


def createConnection(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    sslmode: str = "disable",
) -> TakeoPyTypeORM:
    """Crée une connexion Takeo-ORM (style TypeORM)"""
    return TakeoPyTypeORM(host, port, user, password, database, sslmode)
