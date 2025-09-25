"""
Takeo-ORM Usage Example

This example demonstrates how to use Takeo-ORM to define entities,
establish database connections, and perform CRUD operations.
"""

from takeo_orm import Entity, Column, PrimaryKey, Repository, Connection, ConnectionConfig, ColumnType

# Define entities using decorators
@Entity(table_name="users")
class User:
    """User entity representing the users table"""
    
    id: int = PrimaryKey(auto_increment=True)
    email: str = Column(nullable=False)
    name: str = Column()
    age: int = Column(nullable=True, default=0)
    is_active: bool = Column(default=True)

@Entity(table_name="posts")
class Post:
    """Post entity representing the posts table"""
    
    id: int = PrimaryKey(auto_increment=True)
    title: str = Column(nullable=False)
    content: str = Column(type=ColumnType.TEXT)
    user_id: int = Column(nullable=False)
    created_at: str = Column(type=ColumnType.DATETIME, nullable=True)

def main():
    """Main example function"""
    
    # 1. Configure database connection
    config = ConnectionConfig(
        host="localhost",
        port=5432,
        user="postgres",
        password="password",
        database="takeo_example",
        sslmode="disable"
    )
    
    # Alternative: Load from environment variables
    # config = ConnectionConfig.from_env()
    
    # 2. Establish connection
    connection = Connection(config)
    try:
        connection.connect()
        print("✓ Connected to database successfully")
        
        # Test connection
        if connection.ping():
            print("✓ Database ping successful")
        
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    # 3. Create repositories for entities
    user_repo = Repository(User)
    post_repo = Repository(Post)
    
    print("\n=== CRUD Operations Example ===")
    
    # 4. Create new entities
    print("\n1. Creating new user...")
    new_user = User()
    new_user.email = "john.doe@example.com"
    new_user.name = "John Doe"
    new_user.age = 30
    new_user.is_active = True
    
    try:
        user_repo.save(new_user)
        print("✓ User created successfully")
    except Exception as e:
        print(f"✗ Failed to create user: {e}")
    
    # 5. Create a post
    print("\n2. Creating new post...")
    new_post = Post()
    new_post.title = "My First Post"
    new_post.content = "This is the content of my first post using Takeo-ORM!"
    new_post.user_id = 1  # Assuming user ID 1 exists
    
    try:
        post_repo.save(new_post)
        print("✓ Post created successfully")
    except Exception as e:
        print(f"✗ Failed to create post: {e}")
    
    # 6. Find entities by ID
    print("\n3. Finding user by ID...")
    try:
        found_user = user_repo.find_by_id(1)
        if found_user:
            print(f"✓ Found user: {found_user.name} ({found_user.email})")
        else:
            print("✗ User not found")
    except Exception as e:
        print(f"✗ Failed to find user: {e}")
    
    # 7. Find all entities
    print("\n4. Finding all users...")
    try:
        all_users = user_repo.find_all()
        print(f"✓ Found {len(all_users)} users")
        for user in all_users:
            print(f"  - {user.name} ({user.email})")
    except Exception as e:
        print(f"✗ Failed to find users: {e}")
    
    # 8. Update entity
    print("\n5. Updating user...")
    try:
        user_to_update = User()
        user_to_update.id = 1
        user_to_update.email = "john.updated@example.com"
        user_to_update.name = "John Updated"
        user_to_update.age = 31
        user_to_update.is_active = True
        
        user_repo.update(user_to_update)
        print("✓ User updated successfully")
    except Exception as e:
        print(f"✗ Failed to update user: {e}")
    
    # 9. Delete entity
    print("\n6. Deleting post...")
    try:
        post_repo.delete(1)
        print("✓ Post deleted successfully")
    except Exception as e:
        print(f"✗ Failed to delete post: {e}")
    
    # 10. Close connection
    print("\n=== Cleanup ===")
    connection.close()
    print("✓ Database connection closed")

def demonstrate_advanced_features():
    """Demonstrate advanced Takeo-ORM features"""
    
    print("\n=== Advanced Features Demo ===")
    
    # Complex entity with various column types
    @Entity(table_name="products")
    class Product:
        id: int = PrimaryKey()
        name: str = Column(nullable=False)
        description: str = Column(type=ColumnType.TEXT, nullable=True)
        price: float = Column(type=ColumnType.DECIMAL, default=0.0)
        in_stock: bool = Column(default=True)
        created_at: str = Column(type=ColumnType.DATETIME)
        metadata: bytes = Column(type=ColumnType.BINARY, nullable=True)
    
    print("✓ Advanced entity defined with various column types")
    
    # Repository operations would work the same way
    product_repo = Repository(Product)
    print("✓ Repository created for Product entity")

if __name__ == "__main__":
    print("🚀 Takeo-ORM Usage Example")
    print("=" * 50)
    
    main()
    demonstrate_advanced_features()
    
    print("\n" + "=" * 50)
    print("📚 Example completed!")
    print("\nNext steps:")
    print("1. Set up your PostgreSQL database")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Build Go core: make build")
    print("4. Run your application!")