"""
Test simple Takeo-ORM

Ce test utilise l'API Python de Takeo-ORM (Repository, Entity, Connection)
"""

import os, sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print(
        "[Warning] python-dotenv not installed, using system environment variables only"
    )

# Ajouter le dossier python à sys.path
repo_root = Path(__file__).parent.resolve()
python_dir = repo_root / "python"

if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

print(f"[Test] Répertoire Python: {python_dir}")

# Import de l'API Takeo-ORM haut niveau
try:
    from takeo_orm import (
        Entity,
        Column,
        PrimaryKey,
        Repository,
        Connection,
        ConnectionConfig,
        ColumnType,
    )
    from takeo_orm.connection import set_connection

    print(f"[Test] ✓ Import de l'API Takeo-ORM réussi")

except ImportError as e:
    print(f"[Test] ✗ Erreur import Takeo-ORM: {e}")

    print(f"[Test] Vérifiez que les bindings sont présents dans python/bindings/")

    sys.exit(1)


# Définition des entités avec décorateurs
@Entity(table_name="users")
class User:
    """Entité User avec décorateurs"""

    id: int = PrimaryKey(auto_increment=True)
    name: str = Column(nullable=True)
    email: str = Column(nullable=False)
    age: int = Column(nullable=True, default=25)


@Entity(table_name="posts")
class Post:
    """Entité Post avec décorateurs"""

    id: int = PrimaryKey(auto_increment=True)
    user_id: int = Column(nullable=False)
    title: str = Column(nullable=False)
    content: str = Column(nullable=True)


# Configuration de test (modifiez selon votre base de données)
def get_test_config():
    """Configuration de base de données pour le test"""
    return ConnectionConfig(
        # get in env or use defaults
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "postgres"),
        sslmode=os.getenv("DB_SSLMODE", "disable"),
    )


def test_add_user(user_repo, name, email, age=None):
    """Test d'ajout d'un utilisateur avec Repository"""
    print(f"[Test] Ajout utilisateur: {name} ({email})")

    try:
        # Créer un utilisateur
        user = User()
        user.name = name
        user.email = email
        user.age = age or 25

        # Sauvegarder avec le repository
        user_repo.save(user)
        print(f"[Test] ✓ Utilisateur sauvegardé: {name}")

        # Récupérer l'utilisateur créé pour obtenir son ID généré
        # On cherche par email puisque c'est unique
        print(f"[Test] Recherche de l'ID généré pour {email}...")

        all_users = user_repo.find_all()
        print(f"[Test] Nombre total d'utilisateurs: {len(all_users)}")

        for i, u in enumerate(all_users):
            user_email = getattr(u, "email", "N/A")
            user_id = getattr(u, "id", "N/A")
            print(f"[Test]   User {i+1}: email={user_email}, id={user_id}")

            if hasattr(u, "email") and u.email == email:
                print(f"[Test] ✓ ID généré pour {name}: {getattr(u, 'id', 'N/A')}")

                return u

        print(f"[Test] ⚠ Utilisateur avec email {email} non trouvé dans la liste")

        return user

    except Exception as e:
        print(f"[Test] ✗ Erreur création utilisateur: {e}")

        return None


def test_add_post(post_repo, user_id, title, content):
    """Test d'ajout d'un post avec Repository"""
    print(f"[Test] Ajout post: '{title}' pour user_id={user_id}")

    try:
        # Créer un post
        post = Post()
        post.user_id = user_id
        post.title = title
        post.content = content

        # Sauvegarder avec le repository
        post_repo.save(post)
        print(f"[Test] ✓ Post sauvegardé: {title}")

        return post

    except Exception as e:
        print(f"[Test] ✗ Erreur création post: {e}")

        return None


def test_find_user_by_id(user_repo, user_id):
    """Test de recherche d'un utilisateur par ID"""
    print(f"[Test] Recherche utilisateur ID: {user_id}")

    try:
        user = user_repo.find_by_id(user_id)
        if user:
            print(f"[Test] ✓ Utilisateur trouvé: {user.name} ({user.email})")

            return user
        else:
            print(f"[Test] ✗ Utilisateur ID={user_id} non trouvé")

            return None

    except Exception as e:
        print(f"[Test] ✗ Erreur recherche utilisateur: {e}")

        return None


def test_find_all_users(user_repo):
    """Test de récupération de tous les utilisateurs"""
    print(f"[Test] Récupération de tous les utilisateurs")

    try:
        users = user_repo.find_all()
        print(f"[Test] ✓ {len(users)} utilisateur(s) trouvé(s):")

        for i, user in enumerate(users):
            # Handle age display properly
            age_display = (
                user.age if hasattr(user, "age") and user.age is not None else "N/A"
            )
            print(f"[Test]   {i+1}. {user.name} ({user.email}) - Age: {age_display}")

        return users

    except Exception as e:
        print(f"[Test] ✗ Erreur récupération utilisateurs: {e}")

        return []


def test_update_user(user_repo, user_id, new_name=None, new_age=None):
    """Test de mise à jour d'un utilisateur"""
    print(f"[Test] Mise à jour utilisateur ID: {user_id}")

    try:
        # D'abord récupérer l'utilisateur
        user = user_repo.find_by_id(user_id)
        if not user:
            print(f"[Test] ✗ Utilisateur ID={user_id} non trouvé pour mise à jour")

            return False

        # Modifier les données
        if new_name:
            user.name = new_name
        if new_age:
            user.age = new_age

        # Sauvegarder les modifications
        user_repo.update(user)
        print(f"[Test] ✓ Utilisateur mis à jour: {user.name}")

        return True

    except Exception as e:
        print(f"[Test] ✗ Erreur mise à jour utilisateur: {e}")

        return False


def test_crud_scenarios(connection):
    """Test des scénarios CRUD avec l'API haut niveau - Pattern TypeORM"""
    print(f"\n[Test] === Scénarios CRUD avec Repository (Pattern TypeORM) ===")

    try:
        # PATTERN TYPEORM: Récupérer les repositories via la connexion
        # au lieu de les créer directement
        user_repo = connection.get_repository(User)
        post_repo = connection.get_repository(Post)
        print(f"[Test] ✓ Repositories récupérés via la connexion (comme TypeORM)")

        # Scénario 1: Créer des utilisateurs
        print(f"\n[Test] -- Scénario 1: Création d'utilisateurs --")

        # Utiliser des emails uniques avec timestamp pour éviter les doublons
        import time

        timestamp = int(time.time())
        alice = test_add_user(
            user_repo, "Alice Dupont", f"alice_{timestamp}@example.com", 30
        )
        bob = test_add_user(user_repo, "Bob Martin", f"bob_{timestamp}@example.com", 25)
        charlie = test_add_user(
            user_repo, "Charlie Brown", f"charlie_{timestamp}@example.com", 35
        )

        # Scénario 2: Créer des posts (utiliser les vrais IDs)
        print(f"\n[Test] -- Scénario 2: Création de posts --")

        # Récupérer les IDs réels des utilisateurs créés
        alice_id = getattr(alice, "id", None) if alice else None
        bob_id = getattr(bob, "id", None) if bob else None

        if alice_id:
            test_add_post(
                post_repo, alice_id, "Premier post d'Alice", "Contenu du premier post"
            )
            test_add_post(
                post_repo, alice_id, "Deuxième post d'Alice", "Alice écrit encore"
            )
        else:
            print(f"[Test] ⚠ Alice ID non trouvé, posts ignorés")

        if bob_id:
            test_add_post(
                post_repo, bob_id, "Hello World de Bob", "Bob dit bonjour au monde"
            )
        else:
            print(f"[Test] ⚠ Bob ID non trouvé, post ignoré")

        # Scénario 3: Recherche d'utilisateurs (utiliser les vrais IDs)
        print(f"\n[Test] -- Scénario 3: Recherche d'utilisateurs --")

        alice_id = getattr(alice, "id", None) if alice else None
        if alice_id:
            test_find_user_by_id(user_repo, alice_id)
        else:
            print(f"[Test] ⚠ Alice ID non trouvé, recherche ignorée")

        test_find_user_by_id(user_repo, 999)  # N'existe pas

        # Scénario 4: Liste de tous les utilisateurs
        print(f"\n[Test] -- Scénario 4: Liste de tous les utilisateurs --")

        test_find_all_users(user_repo)

        # Scénario 5: Mise à jour d'un utilisateur (utiliser le vrai ID)
        print(f"\n[Test] -- Scénario 5: Mise à jour d'utilisateur --")

        alice_id = getattr(alice, "id", None) if alice else None
        if alice_id:
            test_update_user(
                user_repo, alice_id, new_name="Alice Dupont-Smith", new_age=31
            )
            # Vérifier la mise à jour
            test_find_user_by_id(user_repo, alice_id)
        else:
            print(f"[Test] ⚠ Alice ID non trouvé, mise à jour ignorée")

        print(f"\n[Test] ✓ Tous les tests CRUD terminés !")

        return True

    except Exception as e:
        print(f"[Test] ✗ Erreur durant les tests CRUD: {e}")

        return False


def main():
    """Fonction principale du test"""
    print(f"[Test] === Test Takeo-ORM avec API Repository ===")

    # Configuration de la connexion
    config = get_test_config()
    print(
        f"[Test] Configuration: {config.user}@{config.host}:{config.port}/{config.database}"
    )

    # Créer et tester la connexion
    try:
        connection = Connection(config)
        connection.connect()
        print(f"[Test] ✓ Connexion établie")

        # Test de ping
        if connection.ping():
            print(f"[Test] ✓ Ping réussi")

        else:
            print(f"[Test] ✗ Ping échoué")

            return

    except Exception as e:
        print(f"[Test] ✗ Erreur de connexion: {e}")
        print(f"[Test] Vérifiez votre configuration dans get_test_config()")
        return

    # Tests CRUD avec Repository
    try:
        crud_success = test_crud_scenarios(connection)

        if crud_success:
            print(f"\n[Test] ✓ Tous les tests sont réussis !")
        else:
            print(f"\n[Test] ✗ Certains tests ont échoué")

    except Exception as e:
        print(f"\n[Test] ✗ Erreur lors des tests: {e}")

    # Fermeture propre
    try:
        connection.close()
        print(f"[Test] ✓ Connexion fermée proprement")

    except Exception as e:
        print(f"[Test] ✗ Erreur fermeture: {e}")

    print(f"\n[Test] === Fin des tests ===")
    print(f"[Test] Note: Ce test utilise l'API Repository de Takeo-ORM,")
    print(
        f"[Test] les entités sont enregistrées automatiquement via les décorateurs @Entity !"
    )


if __name__ == "__main__":
    main()
