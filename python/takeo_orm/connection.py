"""
Database connection management for Takeo-ORM
"""

from typing import Optional
import os

class ConnectionConfig:
    """Database connection configuration"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        database: str = "postgres",
        sslmode: str = "disable"
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.sslmode = sslmode
    
    @classmethod
    def from_env(cls) -> "ConnectionConfig":
        """Create connection config from environment variables"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "postgres"),
            sslmode=os.getenv("DB_SSLMODE", "disable")
        )

class Connection:
    """Database connection wrapper"""
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        self.config = config or ConnectionConfig()
        self._orm_instance = None
        self._connected = False
    
    def connect(self):
        """Establish database connection"""
        if self._connected:
            return
            
        # This will be replaced with actual gopy-generated binding
        # For now, we'll simulate the interface
        try:
            # This would be: from takeo_core import NewTakeoORM
            # self._orm_instance = NewTakeoORM(...)
            print(f"Connecting to {self.config.host}:{self.config.port}/{self.config.database}")
            self._connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    def close(self):
        """Close database connection"""
        if self._orm_instance and hasattr(self._orm_instance, 'Close'):
            self._orm_instance.Close()
        self._connected = False
    
    def ping(self) -> bool:
        """Test database connection"""
        if not self._connected:
            return False
        
        try:
            if self._orm_instance and hasattr(self._orm_instance, 'Ping'):
                self._orm_instance.Ping()
                return True
            return True  # Simulate success for now
        except:
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is established"""
        return self._connected
    
    def get_orm_instance(self):
        """Get the underlying Go ORM instance"""
        if not self._connected:
            raise RuntimeError("Not connected to database")
        return self._orm_instance

# Global connection instance
_default_connection: Optional[Connection] = None

def get_connection() -> Connection:
    """Get the default database connection"""
    global _default_connection
    if _default_connection is None:
        _default_connection = Connection()
    return _default_connection

def set_connection(connection: Connection):
    """Set the default database connection"""
    global _default_connection
    _default_connection = connection