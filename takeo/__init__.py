"""
Takeo-ORM - High-Performance Python ORM with Go Backend
TypeORM-like API with optimized Go bindings
"""

# Import des classes principales
from .orm import Entity, PrimaryGeneratedColumn, Column, createConnection, Repository

__version__ = "0.1.0"
__author__ = "Takeo-ORM Team"
__description__ = "High-Performance Python ORM with Go Backend"

# Exports publics
__all__ = [
    "Entity",
    "PrimaryGeneratedColumn",
    "Column",
    "createConnection",
    "Repository",
]
