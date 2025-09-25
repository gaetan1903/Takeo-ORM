"""
Tests for Takeo-ORM connection management
"""

import pytest
from takeo_orm.connection import Connection, ConnectionConfig


def test_connection_config_creation():
    """Test ConnectionConfig creation with default and custom values"""
    
    # Default config
    config = ConnectionConfig()
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.user == "postgres"
    assert config.sslmode == "disable"
    
    # Custom config
    config = ConnectionConfig(
        host="custom-host",
        port=3306,
        user="custom-user",
        database="custom-db"
    )
    assert config.host == "custom-host"
    assert config.port == 3306
    assert config.user == "custom-user"
    assert config.database == "custom-db"


def test_connection_config_from_env(monkeypatch):
    """Test ConnectionConfig.from_env() method"""
    
    # Set environment variables
    monkeypatch.setenv("DB_HOST", "env-host")
    monkeypatch.setenv("DB_PORT", "3333")
    monkeypatch.setenv("DB_USER", "env-user")
    monkeypatch.setenv("DB_PASSWORD", "env-pass")
    monkeypatch.setenv("DB_NAME", "env-db")
    monkeypatch.setenv("DB_SSLMODE", "require")
    
    config = ConnectionConfig.from_env()
    
    assert config.host == "env-host"
    assert config.port == 3333
    assert config.user == "env-user"
    assert config.password == "env-pass"
    assert config.database == "env-db"
    assert config.sslmode == "require"


def test_connection_creation():
    """Test Connection object creation"""
    
    config = ConnectionConfig(database="test_db")
    connection = Connection(config)
    
    assert connection.config.database == "test_db"
    assert not connection.is_connected


def test_connection_lifecycle():
    """Test connection lifecycle (connect/close)"""
    
    connection = Connection()
    
    # Initially not connected
    assert not connection.is_connected
    
    # Connect (this will just simulate connection for now)
    connection.connect()
    assert connection.is_connected
    
    # Close connection
    connection.close()
    assert not connection.is_connected


def test_connection_ping():
    """Test connection ping functionality"""
    
    connection = Connection()
    
    # Ping without connection should return False
    assert not connection.ping()
    
    # Connect and ping
    connection.connect()
    assert connection.ping()  # Simulated success
    
    # Close and ping again
    connection.close()
    assert not connection.ping()


def test_get_orm_instance_not_connected():
    """Test getting ORM instance when not connected"""
    
    connection = Connection()
    
    with pytest.raises(RuntimeError, match="Not connected to database"):
        connection.get_orm_instance()


def test_get_orm_instance_connected():
    """Test getting ORM instance when connected"""
    
    connection = Connection()
    connection.connect()
    
    # Should not raise an error
    orm_instance = connection.get_orm_instance()
    # For now, this will be None since we're simulating
    assert orm_instance is None


if __name__ == "__main__":
    pytest.main([__file__])