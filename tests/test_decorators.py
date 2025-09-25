"""
Tests for Takeo-ORM Python decorators
"""

import pytest
from takeo_orm.decorators import Entity, Column, PrimaryKey, ColumnMeta, get_entity_metadata
from takeo_orm.types import ColumnType


def test_column_meta_creation():
    """Test ColumnMeta creation with various parameters"""
    
    # Basic column
    col = Column()
    assert isinstance(col, ColumnMeta)
    assert col.nullable is True
    assert col.primary_key is False
    
    # Column with specific parameters
    col = Column(name="custom_name", type=ColumnType.STRING, nullable=False)
    assert col.name == "custom_name"
    assert col.type == "string"
    assert col.nullable is False


def test_primary_key_creation():
    """Test PrimaryKey decorator creation"""
    
    pk = PrimaryKey()
    assert isinstance(pk, ColumnMeta)
    assert pk.primary_key is True
    assert pk.auto_increment is True
    assert pk.nullable is False
    
    # Custom primary key
    pk = PrimaryKey(name="custom_id", auto_increment=False)
    assert pk.name == "custom_id"
    assert pk.auto_increment is False


def test_entity_decorator():
    """Test Entity decorator functionality"""
    
    @Entity(table_name="test_users")
    class TestUser:
        id: int = PrimaryKey()
        name: str = Column(nullable=False)
        email: str = Column(name="email_address")
        age: int
    
    # Check metadata was stored
    metadata = get_entity_metadata(TestUser)
    assert metadata is not None
    assert metadata['table_name'] == "test_users"
    assert 'id' in metadata['columns']
    assert metadata['primary_key'] == 'id'
    
    # Check class has metadata attribute
    assert hasattr(TestUser, '_takeo_metadata')
    assert TestUser._takeo_metadata['table_name'] == "test_users"


def test_entity_without_table_name():
    """Test Entity decorator without explicit table name"""
    
    @Entity()
    class Product:
        id: int = PrimaryKey()
        name: str = Column()
    
    metadata = get_entity_metadata(Product)
    assert metadata['table_name'] == "product"  # lowercase class name


def test_entity_with_mixed_columns():
    """Test entity with various column types"""
    
    @Entity(table_name="mixed_entity")
    class MixedEntity:
        id: int = PrimaryKey(auto_increment=True)
        title: str = Column(nullable=False)
        description: str = Column(type=ColumnType.TEXT)
        price: float = Column(type=ColumnType.DECIMAL, default=0.0)
        active: bool = Column(default=True)
        data: bytes = Column(type=ColumnType.BINARY, nullable=True)
        created_at: str = Column(type=ColumnType.DATETIME)
        plain_field: int  # No column decorator
    
    metadata = get_entity_metadata(MixedEntity)
    
    # Check all columns are registered
    expected_columns = ['id', 'title', 'description', 'price', 'active', 'data', 'created_at', 'plain_field']
    for col in expected_columns:
        assert col in metadata['columns']
    
    # Check primary key
    assert metadata['primary_key'] == 'id'
    
    # Check auto increment
    assert 'id' in metadata['auto_increment_columns']


def test_multiple_entities():
    """Test registering multiple entities"""
    
    @Entity(table_name="authors")
    class Author:
        id: int = PrimaryKey()
        name: str = Column()
    
    @Entity(table_name="books")
    class Book:
        id: int = PrimaryKey()
        title: str = Column()
        author_id: int = Column()
    
    author_metadata = get_entity_metadata(Author)
    book_metadata = get_entity_metadata(Book)
    
    assert author_metadata['table_name'] == "authors"
    assert book_metadata['table_name'] == "books"
    
    # Ensure they're separate
    assert author_metadata != book_metadata


if __name__ == "__main__":
    pytest.main([__file__])