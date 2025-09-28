#!/usr/bin/env python3

import os
from takeo import (
    Entity,
    PrimaryGeneratedColumn,
    Column,
    createConnection,
)


@Entity("users")
class User:
    def __init__(self):
        self.id = None
        self.name = None
        self.email = None
        self.age = None

    id = PrimaryGeneratedColumn()
    name = Column("VARCHAR(100)", nullable=False)
    email = Column("VARCHAR(255)", unique=True, nullable=False)
    age = Column("INTEGER")

    def __str__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}', age={self.age})"


@Entity("posts")
class Post:
    def __init__(self):
        self.id = None
        self.title = None
        self.content = None
        self.author_id = None
        self.published = None

    id = PrimaryGeneratedColumn()
    title = Column("VARCHAR(200)", nullable=False)
    content = Column("TEXT")
    author_id = Column("INTEGER", nullable=False)
    published = Column("BOOLEAN", default="false")

    def __str__(self):
        return f"Post(id={self.id}, title='{self.title}', author_id={self.author_id})"


def main():
    print("🚀 TAKEO-ORM - EXEMPLE COMPLET")
    print("=" * 50)
    print("Syntaxe TypeORM + Performance Go")

    connection = None
    try:
        # TypeORM-style connection with environment variables
        connection = createConnection(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            database=os.getenv("DB_NAME", "orm"),
            sslmode=os.getenv("DB_SSLMODE", "disable"),
        )
        print("✅ Connexion etablie")

        # Repositories TypeORM-style
        userRepo = connection.getRepository(User)
        postRepo = connection.getRepository(Post)

        # Tables
        print("📋 Creation des tables...")
        create_user_result = connection._api.CreateTable("User")
        create_post_result = connection._api.CreateTable("Post")
        print(f"   User table result: {create_user_result}")
        print(f"   Post table result: {create_post_result}")
        print("✅ Tables creees")

        # === DEMO CRUD ===
        print("\n📝 Creation des donnees...")

        # Créer utilisateurs
        user1 = User()
        user1.name = "Alice Dupont"
        user1.email = "alice@example.com"
        user1.age = 28
        saved_user1 = userRepo.save(user1)
        print(f"   👤 {saved_user1}")

        user2 = User()
        user2.name = "Bob Martin"
        user2.email = "bob@example.com"
        user2.age = 32
        saved_user2 = userRepo.save(user2)
        print(f"   👤 {saved_user2}")

        # Créer posts
        post1 = Post()
        post1.title = "Introduction a Takeo-ORM"
        post1.content = "Un ORM performant..."
        post1.author_id = saved_user1.id
        post1.published = True
        saved_post1 = postRepo.save(post1)
        print(f"   📄 {saved_post1}")

        post2 = Post()
        post2.title = "Performance Go-Python"
        post2.content = "Bindings optimises..."
        post2.author_id = saved_user2.id
        post2.published = False
        saved_post2 = postRepo.save(post2)
        print(f"   📄 {saved_post2}")

        # === LECTURE ===
        print("\n📖 Lecture des donnees...")
        all_users = userRepo.find()
        all_posts = postRepo.find()
        print(f"   Utilisateurs: {len(all_users)} - {all_users}")
        print(f"   Posts: {len(all_posts)} - {all_posts}")

        # FindOne
        user = userRepo.findOne(saved_user1.id)
        if user:
            print(f"   User ID 1: {user}")

        # === UPDATE ===
        print("\n✏️  Mise a jour...")
        userRepo.update(saved_user1.id, {"age": 29})
        updated_user = userRepo.findOne(saved_user1.id)
        print(f"   Age mis a jour: {updated_user}")

        # === DELETE ===
        print("\n🗑️  Suppression...")
        postRepo.delete(saved_post2.id)
        remaining_posts = postRepo.find()
        print(f"   Posts restants: {len(remaining_posts)}")

        print(f"\n" + "=" * 50)
        print("🎉 DEMONSTRATION TERMINEE!")
        print("✨ Takeo-ORM: TypeORM + Go Performance")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if connection:
            try:
                connection._api.DropTable("Post")
                connection._api.DropTable("User")
                print("\n🧹 Tables supprimees")
            except:
                pass
            connection.close()
            print("🔌 Connexion fermee")


if __name__ == "__main__":
    main()
