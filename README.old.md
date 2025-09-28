
# Takeo-ORM

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Go 1.19+](https://img.shields.io/badge/go-1.19+-00ADD8.svg)](https://golang.org/)

Un ORM ultra-performant pour Python avec backend Go optimisé, offrant une API simple inspirée de TypeORM.

## 🚀 Caractéristiques

- **Performance maximale** : Architecture Go-centric avec bindings directs
- **API intuitive** : Inspirée de TypeORM, familière et simple
- **Opérations batch** : Optimisations pour les traitements en masse
- **PostgreSQL natif** : Support complet avec transactions
- **Double architecture** : API optimisée + legacy pour migration

## 📊 Performance

L'architecture optimisée de Takeo-ORM offre des gains de performance significatifs:

- **14-33x plus rapide** que l'API legacy
- **Opérations batch natives** pour les traitements en masse
- **Bindings Go directs** éliminant l'overhead Python
- **Transactions optimisées** avec prepared statements

## � Installation Rapide

```bash
# Cloner le projet
git clone <repo-url>
cd Takeo-ORM

# Build avec l'architecture optimisée
./build_optimized.sh  # Linux/Mac
# ou
.\build_optimized.ps1  # Windows
```

## � Usage - API Optimisée

```python
from python.takeo_py import TakeoPy, entity, column, primary_key, setup_entity_metadata

# Définir une entité
@entity(name="User", table_name="users")
class User:
    def __init__(self):
        self.id = None
        self.name = None
        self.email = None
    
    @primary_key()
    @column("id", "SERIAL PRIMARY KEY")
    def get_id(self): return self.id
    
    @column("name", "VARCHAR(100) NOT NULL")
    def get_name(self): return self.name
    
    @column("email", "VARCHAR(255) UNIQUE")
    def get_email(self): return self.email

setup_entity_metadata(User)

# Connexion et usage
takeo = TakeoPy(
    host="localhost", port=5432, 
    user="postgres", password="password", 
    database="mydb"
)

takeo.register_entity(User)
takeo.create_table(User)

# CRUD optimisé
user = User()
user.name = "Alice"
user.email = "alice@example.com"

# Opérations individuelles
user_id = takeo.save(user)
found_user = takeo.find_by_id(User, user_id)
takeo.update(User, user_id, name="Alice Updated")

# Opérations batch (performance maximale)
users_batch = [create_user(i) for i in range(1000)]
batch_ids = takeo.save_batch(users_batch)
takeo.update_batch(User, batch_updates)
takeo.delete_batch(User, batch_ids)

# Transactions
with takeo.begin_transaction() as tx:
    tx.save(user)
    # Auto-commit/rollback
```

## 📈 Benchmarks

Testez les performances vous-même:

```bash
# Benchmark complet vs autres ORMs
python benchmark_crud.py

# Comparaison architecture optimisée vs legacy  
python benchmark_optimized.py

# Test simple
python example_optimized.py
```

## 🏗️ Architecture

**API Optimisée (Recommandée)**:
- `TakeoPy` : Interface Python haut niveau
- Bindings Go directs via `gopy`
- Performance maximale

**API Legacy (Migration)**:
- `Repository` : Pattern repository classique
- Compatible avec code existant
- Migration progressive possible

## 📋 Exemples Complets

- `example_optimized.py` : Démonstration API optimisée
- `example.py` : Usage API legacy
- `benchmark_crud.py` : Comparaisons avec SQLAlchemy/Peewee

## 🛠️ Développement

```bash
# Tests
python -m pytest tests/

# Build custom
cd core && go build -buildmode=c-shared -o takeo_core.so .
gopy build -output=python/bindings -vm=python3 ./core
```

Voir `docs/` pour l'architecture détaillée et les guides de contribution.
