
# Takeo-ORM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Go 1.19+](https://img.shields.io/badge/go-1.19+-00ADD8.svg)](https://golang.org/)

A high-performance Object-Relational Mapper (ORM) for Python with a Go core. Inspired by TypeORM, it provides a familiar decorator-based API while leveraging Go's performance for database operations.

## 🚀 Features

- **High Performance**: Core database operations implemented in Go for maximum speed
- **TypeORM-like API**: Familiar decorator syntax for Python developers
- **PostgreSQL Support**: Optimized for PostgreSQL databases
- **Repository Pattern**: Clean separation of data access logic
- **Type Safety**: Full type annotations and compile-time checking
- **Easy Setup**: Minimal configuration required

## 📦 Installation

### Prerequisites

- Go 1.19+
- Python 3.8+
- PostgreSQL 12+
- gopy (for Python-Go bindings)

### Build from Source

```bash
git clone https://github.com/gaetan1903/Takeo-ORM.git
cd Takeo-ORM

# Linux/MacOS
./build.sh

# Windows
.\build.ps1
```

## 🚀 Quick Start

### 1. Define Your Entities

```python
from takeo_orm import Entity, Column, PrimaryKey

@Entity(table_name="users")
class User:
    id: int = PrimaryKey(auto_increment=True)
    name: str = Column()
    email: str = Column(nullable=False)
    age: int = Column(default=25)
```

### 2. Configure Database Connection

```python
from takeo_orm import Connection, ConnectionConfig

config = ConnectionConfig(
    host="localhost",
    port=5432,
    user="postgres",
    password="your_password",
    database="takeo_orm",
    sslmode="disable"
)

connection = Connection(config)
connection.connect()
```

### 3. Perform CRUD Operations

```python
# Get repository
user_repo = connection.get_repository(User)

# Create
user = User()
user.name = "Alice"
user.email = "alice@example.com"
user_repo.save(user)

# Read
found_user = user_repo.find_by_id(user.id)
all_users = user_repo.find_all()

# Update
found_user.age = 30
user_repo.update(found_user)

# Delete
user_repo.delete(user.id)
```

## 🧪 Testing

Run the example script to test all CRUD operations:

```bash
python3 example.py
```

## 📚 Documentation

- **[Usage Guide](docs/usage.md)**: Complete usage documentation with simple and advanced examples
- **[API Reference](docs/api.md)**: Detailed API documentation
- **[Roadmap](docs/roadmap.md)**: Development roadmap and future plans

## 🏗️ Project Structure

```
Takeo-ORM/
├── core/                    # Go core implementation
│   ├── db.go               # Database connection management
│   ├── entity.go           # Entity metadata and reflection
│   ├── repository.go       # CRUD operations
│   └── takeo.go            # Main API for gopy export
├── python/                 # Python API layer
│   └── takeo_orm/
│       ├── __init__.py
│       ├── decorators.py   # Entity and column decorators
│       ├── repository.py   # Repository pattern
│       ├── connection.py   # Connection management
│       └── types.py       # Type definitions
├── docs/                   # Documentation
├── tests/                  # Test suites
├── example.py              # Usage example
├── Makefile               # Build automation
└── README.md              # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [TypeORM](https://typeorm.io/) for API design
- Built with [gopy](https://github.com/go-python/gopy) for Python-Go integration
- Uses [lib/pq](https://github.com/lib/pq) for PostgreSQL connectivity

---

**Made with ❤️ for the Python communities**
