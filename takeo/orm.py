"""
Takeo-ORM - TypeORM-like API for Python
High-performance ORM with Go backend and TypeORM-inspired syntax
"""

import json
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
            columns_json = json.dumps(columns_dict)
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
        entity_json = json.dumps(entity_data)

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
                data = json.loads(json_to_parse)
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
                data = json.loads(json_to_parse)
                if isinstance(data, list):
                    return [self._dict_to_entity(item) for item in data]
            except json.JSONDecodeError as e:
                raise Exception(f"JSON decode error: {e}")
        return []

    def update(self, id: int, update_data: Dict[str, Any]):
        """Met à jour une entité (style TypeORM)"""
        update_json = json.dumps(update_data)
        result = self._api.Update(self.entity_class.__name__, id, update_json)
        if result:
            raise Exception(f"Update error: {result}")

    def delete(self, id: int):
        """Supprime une entité (style TypeORM)"""
        result = self._api.Delete(self.entity_class.__name__, id)
        if result:
            raise Exception(f"Delete error: {result}")

    def _entity_to_dict(self, entity) -> Dict[str, Any]:
        """Convertit une entité en dictionnaire"""
        result = {}
        for attr_name, col_meta in self.entity_class._takeo_columns.items():
            if hasattr(entity, attr_name):
                value = getattr(entity, attr_name)
                if value is not None:
                    result[col_meta["name"]] = value
        return result

    def _dict_to_entity(self, data: Dict[str, Any]):
        """Convertit un dictionnaire en entité"""
        entity = self.entity_class()
        for attr_name, col_meta in self.entity_class._takeo_columns.items():
            column_name = col_meta["name"]
            if column_name in data:
                setattr(entity, attr_name, data[column_name])
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
