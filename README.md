<div align="center">

# 🚀 Takeo-ORM

**High-Performance Python ORM** • *TypeORM Syntax + Go Backend*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Go 1.19+](https://img.shields.io/badge/go-1.19+-00ADD8.svg)](https://golang.org/)
[![Development Status](https://img.shields.io/badge/Status-Active%20Development-orange.svg)]()

*Familiar TypeORM decorators with Go backend optimization*

</div>

---

## ⚡ Why Choose Takeo-ORM?

<table>
<tr>
<td width="50%">

### 🎯 **Developer Experience**
- 💎 **TypeORM-like syntax** you already know
- ��️ **Zero configuration** - works out of the box
- 📦 **Auto table management** - no migrations needed

</td>
<td width="50%">

### 🚀 **Performance Goals**
- 🎯 **Aiming to be fastest** Python ORM
- 🔥 **Native Go backend** with optimized queries
- 🏆 **Prepared statements** and connection pooling
- 📊 **Transparent benchmarks** - see real performance below

</td>
</tr>
</table>

## 🎨 Beautiful Syntax

```python
from takeo import Entity, PrimaryGeneratedColumn, Column, createConnection

@Entity("users")
class User:
    id = PrimaryGeneratedColumn()
    name = Column("VARCHAR(100)", nullable=False)
    email = Column("VARCHAR(255)", unique=True)

# TypeORM-style usage
connection = createConnection(database="myapp")
userRepo = connection.getRepository(User)

# Elegant CRUD operations
user = User()
user.name = "Alice"
saved = userRepo.save(user)        # 💾 Create
users = userRepo.find()            # 📖 Read  
userRepo.update(1, {"age": 25})    # ✏️  Update
userRepo.delete(1)                 # 🗑️  Delete
```

## 🚀 Quick Start

```bash
# 1️⃣ Clone and build
git clone https://github.com/gaetan1903/Takeo-ORM.git
cd Takeo-ORM && chmod +x build.sh && ./build.sh

# 2️⃣ Set up environment (optional)
cp .env.example .env  # Edit with your DB settings

# 3️⃣ Run the example
python example.py
```

## 📊 Performance Benchmarks

*Real performance results (10,000 records, 5 iterations on PostgreSQL):*

| Operation | Takeo-ORM | SQLAlchemy | Current Status |
|-----------|-----------|------------|----------------|
| **INSERT 10K records** | 17,950ms | 1,147ms | **15.7x slower** ⚠️ |
| **READ 10K records** | 87ms | 148ms | **1.7x faster** ✅ |
| **UPDATE operations** | 190ms | 129ms | **1.5x slower** ⚠️ |
| **DELETE operations** | 169ms | 220ms | **1.3x faster** ✅ |

### 🎯 **Current Performance Profile**
- ✅ **READ operations**: **70% faster** than SQLAlchemy
- ✅ **DELETE operations**: **30% faster** than SQLAlchemy  
- ⚠️ **INSERT operations**: **15x slower** due to gopy communication overhead
- ⚠️ **UPDATE operations**: **50% slower** due to individual API calls
- 🚧 **Overall**: Currently optimized for read-heavy workloads

### 📈 **Performance Analysis**
- **Strong suit**: Query operations (SELECT, DELETE)
- **Bottleneck**: Write operations due to Python ↔ Go bindings
- **Best use case**: Read-heavy applications, data analytics
- **Avoid for**: High-frequency writes, bulk data ingestion

*Run `python benchmark.py` to verify these results on your system.*

## 🛠️ API Reference

### Entity Decorators
```python
@Entity("table_name")           # Define database entity
id = PrimaryGeneratedColumn()   # Auto-increment primary key  
name = Column("VARCHAR(100)", nullable=False, unique=True)
```

### Repository Operations
```python
repo = connection.getRepository(User)
entity = repo.save(user)        # Create/Update
entity = repo.findOne(1)        # Find by ID
entities = repo.find()          # Find all
repo.update(1, changes)         # Partial update
repo.delete(1)                  # Delete by ID
```

## 🚧 Development Roadmap

### **🎯 Performance Goals**
Our goal is to become the fastest Python ORM. Current challenges and solutions:

**Current Bottlenecks:**
- 🔧 **gopy bindings overhead** (99.9% of execution time)
- 📡 **JSON serialization** between Python ↔ Go
- 🔄 **Individual API calls** instead of batch operations

**Planned Optimizations:**
- 🚀 **gRPC communication** replacing gopy bindings
- 🗜️ **Protocol Buffers** for binary serialization
- ⚡ **True batch operations** with single database round-trips
- 🔄 **Connection pooling** and prepared statement caching

### **✅ Recent Improvements**
- 📈 **18% faster READ operations** vs SQLAlchemy
- 🔧 **Prepared statements pool** for query optimization
- ⚡ **orjson integration** for faster JSON processing
- 🗃️ **Optimized entity conversions** with caching

## 🤝 Contributing

Help us reach our performance goals!

```bash
git clone <your-fork>
./build.sh              # Build bindings
python benchmark.py     # Run performance tests
python -m pytest tests/ # Run tests
```

**Priority Areas:**
- 🚀 gRPC/Protobuf implementation
- ⚡ Batch operation optimization  
- 📊 More comprehensive benchmarks

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for developers who value simplicity and performance**

⭐ *Star us if Takeo-ORM helps you build faster!* ⭐

</div>
