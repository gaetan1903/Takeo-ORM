"""
Type definitions for Takeo-ORM
"""

from enum import Enum
from typing import Any, Dict, Union

class ColumnType(Enum):
    """Database column types"""
    INTEGER = "int"
    STRING = "string"
    TEXT = "string"
    BOOLEAN = "bool"
    FLOAT = "float64"
    DECIMAL = "float64"
    DATETIME = "time.Time"
    DATE = "time.Time"
    TIME = "time.Time"
    BINARY = "[]byte"

# Type aliases for convenience
EntityDict = Dict[str, Any]
ColumnDict = Dict[str, str]
ValueDict = Dict[str, Any]