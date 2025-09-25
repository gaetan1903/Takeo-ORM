# Takeo-ORM

Takeo-ORM is a high-performance Object-Relational Mapper (ORM) for Python, with its core implemented in Go for maximum efficiency and speed. Inspired by the developer experience of TypeORM (Node.js/TypeScript), it provides a familiar decorator-based API while leveraging Go's performance for database operations.

## 🚀 Features

- **High Performance**: Core database operations implemented in Go for maximum speed
- **Familiar API**: TypeORM-inspired decorator syntax for Python developers
- **Type Safety**: Full type annotations and compile-time checking
- **PostgreSQL First**: Optimized for PostgreSQL with plans for multi-database support
- **Simple Setup**: Minimal configuration required to get started
- **Repository Pattern**: Clean separation of data access logic

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python API    │    │   Gopy Bridge    │    │   Go Core       │
│                 │    │                  │    │                 │
│ • Decorators    │◄──►│ • Type Mapping   │◄──►│ • DB Pool       │
│ • Repository    │    │ • Error Handling │    │ • Query Builder │
│ • Connection    │    │ • Memory Mgmt    │    │ • CRUD Ops      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/gaetan1903/Takeo-ORM.git
cd Takeo-ORM

# Install dependencies and build
make install-deps
make build

# Or for development setup
make dev-setup
```

## 🚀 Quick Start

### 1. Define Your Entities

```python
from takeo_orm import Entity, Column, PrimaryKey, ColumnType

@Entity(table_name="users")
class User:
    id: int = PrimaryKey(auto_increment=True)
    email: str = Column(nullable=False)
    name: str = Column()
    age: int = Column(nullable=True, default=0)
    is_active: bool = Column(default=True)

@Entity(table_name="posts")
class Post:
    id: int = PrimaryKey(auto_increment=True)
    title: str = Column(nullable=False)
    content: str = Column(type=ColumnType.TEXT)
    user_id: int = Column(nullable=False)
```

### 2. Configure Database Connection

```python
from takeo_orm import Connection, ConnectionConfig

config = ConnectionConfig(
    host="localhost",
    port=5432,
    user="postgres",
    password="password",
    database="myapp",
    sslmode="disable"
)

connection = Connection(config)
connection.connect()
```

### 3. Perform CRUD Operations

```python
from takeo_orm import Repository

# Create repositories
user_repo = Repository(User)
post_repo = Repository(Post)

# Create new entities
user = User()
user.email = "john@example.com"
user.name = "John Doe"
user.age = 30

user_repo.save(user)

# Find entities
found_user = user_repo.find_by_id(1)
all_users = user_repo.find_all()

# Update entities
found_user.age = 31
user_repo.update(found_user)

# Delete entities
user_repo.delete(1)
```

## 🛠️ Development

### Prerequisites

- Go 1.19+ 
- Python 3.8+
- PostgreSQL 12+
- gopy for Python-Go bindings

### Build Commands

```bash
# Install dependencies
make install-deps

# Build Go core
make build-go

# Generate Python bindings
make build-bindings

# Build everything
make build

# Run tests
make test

# Run example
make example

# Clean build artifacts
make clean
```

### Project Structure

```
Takeo-ORM/
├── core/                 # Go core implementation
│   ├── db.go            # Database connection management
│   ├── entity.go        # Entity metadata and reflection
│   ├── repository.go    # CRUD operations
│   └── takeo.go         # Main API for gopy export
├── python/              # Python API layer
│   └── takeo_orm/
│       ├── __init__.py
│       ├── decorators.py # Entity and column decorators
│       ├── repository.py # Repository pattern
│       ├── connection.py # Connection management
│       └── types.py     # Type definitions
├── examples/            # Usage examples
├── tests/              # Test suites
├── docs/               # Documentation
├── Makefile           # Build automation
├── setup.py           # Python package setup
└── requirements.txt   # Python dependencies
```

## 📚 Documentation

- **[Usage Example](examples/usage_example.py)**: Complete example showing all features
- **[Roadmap](docs/roadmap.md)**: Development roadmap and future plans
- **[API Reference](docs/api.md)**: Detailed API documentation (coming soon)
- **[Contributing Guide](docs/contributing.md)**: How to contribute (coming soon)

## 🎯 Roadmap to MVP

### Phase 1: Foundation ✅
- [x] Go core implementation with PostgreSQL support
- [x] Python decorator API design
- [x] Repository pattern
- [x] Basic CRUD operations
- [x] Project structure and build system

### Phase 2: Integration (In Progress)
- [ ] Gopy binding generation
- [ ] End-to-end integration testing
- [ ] Error handling across language boundaries
- [ ] Memory management optimization

### Phase 3: Polish & Release
- [ ] Performance benchmarks
- [ ] Complete documentation
- [ ] PyPI package release
- [ ] Community building

## 🔧 Current Status

**⚠️ Alpha Stage**: Takeo-ORM is currently in active development. The Go core is functional, and the Python API is designed, but the gopy integration is still in progress. 

**What Works:**
- ✅ Go core with full CRUD operations
- ✅ Python decorator API design
- ✅ Repository pattern implementation
- ✅ Build system and project structure

**In Progress:**
- 🔨 Gopy binding generation
- 🔨 Python-Go integration testing
- 🔨 Error handling and type conversion

## 🤝 Contributing

We welcome contributions! Here are some ways you can help:

- **Testing**: Try the examples and report issues
- **Documentation**: Improve docs and examples
- **Features**: Implement planned features from the roadmap
- **Performance**: Optimize Go core operations
- **Integration**: Help with gopy binding challenges

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [TypeORM](https://typeorm.io/) for API design
- Built with [gopy](https://github.com/go-python/gopy) for Python-Go integration  
- Uses [lib/pq](https://github.com/lib/pq) for PostgreSQL connectivity

## 📞 Support

- **Issues**: Report bugs and feature requests on [GitHub Issues](https://github.com/gaetan1903/Takeo-ORM/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/gaetan1903/Takeo-ORM/discussions)
- **Email**: Contact the maintainers at info@takeo-orm.dev

---

**Made with ❤️ for the Python and Go communities**
