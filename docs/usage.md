# Takeo-ORM Usage Guide

This guide provides comprehensive examples of using Takeo-ORM, from basic CRUD operations to advanced features.

## Table of Contents

- [Simple Usage](#simple-usage)
- [Advanced Usage](#advanced-usage)
- [Entity Definition](#entity-definition)
- [Repository Operations](#repository-operations)
- [Connection Management](#connection-management)
- [Error Handling](#error-handling)

## Simple Usage

### Basic Setup

```python
from takeo_orm import Entity, Column, PrimaryKey, Connection, ConnectionConfig

# Define an entity
@Entity(table_name="users")
class User:
    id: int = PrimaryKey(auto_increment=True)
    name: str = Column()
    email: str = Column(nullable=False)

# Configure connection
config = ConnectionConfig(
    host="localhost",
    port=5432,
    user="postgres",
    password="your_password",
    database="takeo_orm",
    sslmode="disable"
)

# Connect and get repository
connection = Connection(config)
connection.connect()
user_repo = connection.get_repository(User)
```

### Basic CRUD Operations

```python
# Create
user = User()
user.name = "John Doe"
user.email = "john@example.com"
user_repo.save(user)

# Read
user_from_db = user_repo.find_by_id(user.id)
all_users = user_repo.find_all()

# Update
user_from_db.name = "John Smith"
user_repo.update(user_from_db)

# Delete
user_repo.delete(user.id)
```

## Advanced Usage

### Complex Entities

```python
from takeo_orm import Entity, Column, PrimaryKey, ColumnType

@Entity(table_name="posts")
class Post:
    id: int = PrimaryKey(auto_increment=True)
    title: str = Column(nullable=False)
    content: str = Column(type=ColumnType.TEXT)
    user_id: int = Column(nullable=False)
    created_at: str = Column(default="NOW()")
    published: bool = Column(default=False)

@Entity(table_name="comments")
class Comment:
    id: int = PrimaryKey(auto_increment=True)
    post_id: int = Column(nullable=False)
    author: str = Column(nullable=False)
    content: str = Column()
    created_at: str = Column(default="NOW()")
```

### Repository with Multiple Entities

```python
# Get repositories for all entities
user_repo = connection.get_repository(User)
post_repo = connection.get_repository(Post)
comment_repo = connection.get_repository(Comment)

# Create a user
user = User()
user.name = "Alice"
user.email = "alice@example.com"
user_repo.save(user)

# Create a post for that user
post = Post()
post.title = "My First Post"
post.content = "This is the content of my first post."
post.user_id = user.id  # Use the real ID from saved user
post_repo.save(post)

# Add a comment to the post
comment = Comment()
comment.post_id = post.id
comment.author = "Bob"
comment.content = "Great post!"
comment_repo.save(comment)
```

### Batch Operations

```python
# Save multiple entities
users = []
for i in range(10):
    user = User()
    user.name = f"User {i}"
    user.email = f"user{i}@example.com"
    users.append(user)

# Note: Current version saves one by one
for user in users:
    user_repo.save(user)

# Find all with filtering (future feature)
# all_users = user_repo.find_all(where={"active": True})
```

### Custom Repository Methods

```python
# You can extend the repository for custom methods
class UserRepository:
    def __init__(self, connection):
        self.repo = connection.get_repository(User)

    def find_by_email(self, email: str):
        # Custom method - find all and filter
        all_users = self.repo.find_all()
        for user in all_users:
            if user.email == email:
                return user
        return None

    def find_adults(self):
        # Find users 18+
        all_users = self.repo.find_all()
        return [u for u in all_users if getattr(u, 'age', 0) >= 18]

# Usage
custom_repo = UserRepository(connection)
user = custom_repo.find_by_email("alice@example.com")
adults = custom_repo.find_adults()
```

## Entity Definition

### Column Types

```python
from takeo_orm import ColumnType

class Article:
    id: int = PrimaryKey(auto_increment=True)
    title: str = Column(nullable=False, max_length=200)
    content: str = Column(type=ColumnType.TEXT)  # For large text
    published: bool = Column(default=False)
    view_count: int = Column(default=0)
    created_at: str = Column(default="NOW()")
```

### Relationships (Future Feature)

```python
# Planned for future versions
@Entity(table_name="posts")
class Post:
    id: int = PrimaryKey(auto_increment=True)
    title: str = Column(nullable=False)
    author: User = ManyToOne(User)  # Not yet implemented
    comments: List[Comment] = OneToMany(Comment)  # Not yet implemented
```

## Repository Operations

### Available Methods

```python
# Save/Create
repo.save(entity)

# Find by ID
entity = repo.find_by_id(entity_id)

# Find all
entities = repo.find_all()

# Update
repo.update(entity)

# Delete
repo.delete(entity_id)
```

### Working with Primary Keys

```python
# Auto-increment primary keys
user = User()
user.name = "Alice"
user_repo.save(user)
print(f"Generated ID: {user.id}")  # ID is set after save

# Manual primary keys (future feature)
# @Entity(table_name="categories")
# class Category:
#     id: str = PrimaryKey()  # String primary key
#     name: str = Column(nullable=False)
```

## Connection Management

### Connection Configuration

```python
config = ConnectionConfig(
    host="localhost",      # Database host
    port=5432,            # Database port
    user="postgres",      # Database user
    password="secret",    # Database password
    database="myapp",     # Database name
    sslmode="disable"     # SSL mode: disable, require, verify-ca, verify-full
)
```

### Connection Lifecycle

```python
connection = Connection(config)

# Connect
connection.connect()

# Check connection
if connection.ping():
    print("Database connected!")

# Use repositories...
user_repo = connection.get_repository(User)
# ... operations ...

# Close connection
connection.close()
```

### Connection Pooling (Future Feature)

```python
# Planned for future versions
config = ConnectionConfig(
    # ... other settings ...
    max_connections=10,
    min_connections=2
)
```

## Error Handling

### Basic Error Handling

```python
try:
    user_repo.save(user)
    print("User saved successfully")
except Exception as e:
    print(f"Failed to save user: {e}")

try:
    user = user_repo.find_by_id(user_id)
    if user:
        print(f"Found user: {user.name}")
    else:
        print("User not found")
except Exception as e:
    print(f"Error finding user: {e}")
```

### Connection Errors

```python
try:
    connection = Connection(config)
    connection.connect()
except Exception as e:
    print(f"Connection failed: {e}")
    # Handle connection failure
    exit(1)
```

### Validation Errors

```python
# Entity validation (future feature)
try:
    invalid_user = User()
    # Missing required email
    user_repo.save(invalid_user)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Best Practices

### 1. Always Close Connections

```python
connection = Connection(config)
try:
    connection.connect()
    # ... use connection ...
finally:
    connection.close()
```

### 2. Use Meaningful Entity Names

```python
# Good
@Entity(table_name="user_profiles")
class UserProfile:
    pass

# Avoid
@Entity(table_name="tbl_usr")
class Usr:
    pass
```

### 3. Handle Primary Keys Properly

```python
# Always use the ID returned after save
user = User()
user.name = "Alice"
user_repo.save(user)

# Use user.id for relationships
post = Post()
post.user_id = user.id  # Correct
post_repo.save(post)
```

### 4. Batch Operations Carefully

```python
# For large datasets, consider batching
users = []
for i in range(1000):
    user = User()
    user.name = f"User {i}"
    users.append(user)

# Save in batches of 100
batch_size = 100
for i in range(0, len(users), batch_size):
    batch = users[i:i + batch_size]
    for user in batch:
        user_repo.save(user)
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check PostgreSQL is running
   - Verify connection parameters
   - Check firewall settings

2. **Entity Not Registered**
   - Ensure `@Entity` decorator is used
   - Check table name spelling

3. **Primary Key Errors**
   - Ensure primary key is set for updates/deletes
   - Use the ID returned after save

4. **Type Conversion Errors**
   - Ensure column types match Python types
   - Check nullable constraints

### Debug Mode

Enable debug logging (future feature):

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Takeo-ORM will log detailed operations
```

## Migration from Other ORMs

### From SQLAlchemy

```python
# SQLAlchemy
# user = User(name="Alice", email="alice@example.com")
# session.add(user)
# session.commit()

# Takeo-ORM
user = User()
user.name = "Alice"
user.email = "alice@example.com"
user_repo.save(user)
```

### From Django ORM

```python
# Django
# user = User.objects.create(name="Alice", email="alice@example.com")

# Takeo-ORM
user = User()
user.name = "Alice"
user.email = "alice@example.com"
user_repo.save(user)
```

## Performance Tips

1. **Connection Reuse**: Reuse connections instead of creating new ones
2. **Batch Operations**: Group multiple operations when possible
3. **Indexing**: Ensure proper database indexes on frequently queried columns
4. **Connection Pooling**: Use connection pooling for high-traffic applications (future feature)

## Next Steps

- Check the [API Reference](api.md) for detailed method signatures
- Explore the [example.py](../example.py) file for a complete working example
- Join our [GitHub Discussions](https://github.com/gaetan1903/Takeo-ORM/discussions) for questions