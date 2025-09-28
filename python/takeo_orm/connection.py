"""
Database connection management for Takeo-ORM
"""

from typing import Optional
import os
import sys
import platform

# Add bindings to Python path
bindings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bindings")
if bindings_path not in sys.path:
    sys.path.insert(0, bindings_path)

# Import the Go bindings as a proper package
#
# Notes about where NewTakeoORM can live and how to import it:
# 1) Typical case (recommended): gopy generated a Python package (go.py/core.py
#    plus a compiled extension like `_takeo_core...so`). In that case there is a
#    small Python wrapper module (go.py or core.py) which imports the compiled
#    extension. You can import the exported constructor directly from the
#    generated package. Examples:
#
#    # If bindings are available as a top-level package named `bindings`:
#    from bindings import NewTakeoORM
#
#    # If bindings are placed inside a package (e.g. takeo_orm.bindings):
#    from takeo_orm.bindings import NewTakeoORM
#
# 2) If you only have the compiled extension `_takeo_core*.so` but no wrapper
#    Python files (go.py/core.py), gopy's wrapper code is missing — the .so
#    exports low-level symbols and is not directly usable as a high-level
#    Python class. The recommended fix is to (re)generate the wrappers with
#    gopy so that `go.py` / `core.py` are present. Example commands (run from
#    the repo root in WSL/Linux):
#
#    gopy build -output=temp_bindings -name=takeo_core ./core
#    python3 temp_bindings/build.py  # will compile the shared object
#    cp temp_bindings/go.py examples/takeo_orm/bindings/
#    cp temp_bindings/core.py examples/takeo_orm/bindings/ || true
#    cp temp_bindings/_takeo_core*.so examples/takeo_orm/bindings/
#
# 3) Advanced: if go.py/core.py exist but import path is wrong, you can load
#    the wrapper module dynamically (example):
#
#    import importlib.util, importlib.machinery, sys
#    spec = importlib.util.spec_from_file_location('takeo_core_wrapper', '/abs/path/to/go.py')
#    module = importlib.util.module_from_spec(spec)
#    sys.modules['takeo_core_wrapper'] = module
#    spec.loader.exec_module(module)
#    NewTakeoORM = module.NewTakeoORM
#
# In this file we attempt the standard package import and raise a clear error if
# it fails so the user knows to (re)generate or place the bindings.
try:
    # Import bindings as a package to handle relative imports correctly
    import bindings
    from bindings.core import NewTakeoORM
except ImportError as e:
    raise ImportError(
        f"Could not import Go bindings: {e}\n"
        f"OS detected: {platform.system()}\n"
        "If NewTakeoORM is inside the compiled .so but no wrapper Python files exist,\n"
        "re-run gopy to generate the Python wrappers and compiled extension (see README).\n"
    ) from e


class ConnectionConfig:
    """Database connection configuration"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        database: str = "postgres",
        sslmode: str = "disable",
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
            sslmode=os.getenv("DB_SSLMODE", "disable"),
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

        try:
            # Create Go ORM instance using bindings
            self._orm_instance = NewTakeoORM(
                self.config.host,
                self.config.port,
                self.config.user,
                self.config.password,
                self.config.database,
                self.config.sslmode,
            )

            # Test the connection
            self._orm_instance.Ping()
            self._connected = True
            print(
                f"Connected to {self.config.host}:{self.config.port}/{self.config.database}"
            )

        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def close(self):
        """Close database connection"""
        if self._orm_instance:
            try:
                self._orm_instance.Close()
            except Exception as e:
                print(f"Warning: Error closing connection: {e}")
        self._connected = False
        self._orm_instance = None

    def ping(self) -> bool:
        """Test database connection"""
        if not self._connected or not self._orm_instance:
            return False

        try:
            self._orm_instance.Ping()
            return True
        except Exception as e:
            print(f"Ping failed: {e}")
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

    def get_repository(self, entity_class):
        """
        Get a repository for an entity class (TypeORM pattern)

        This follows the TypeORM pattern where repositories are obtained
        from the connection/data source rather than created directly.

        Args:
            entity_class: The entity class (decorated with @Entity)

        Returns:
            Repository instance tied to this connection
        """
        # Import here to avoid circular imports
        from .repository import Repository

        return Repository(entity_class, self)


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
