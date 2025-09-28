#!/usr/bin/env python3
"""
Takeo-ORM vs SQLAlchemy Performance Benchmark
Compares real-world performance between Takeo-ORM and SQLAlchemy
"""

import os
import time
import statistics
import asyncio
from typing import List
import psycopg2
from contextlib import contextmanager

# Test configuration
TEST_RECORDS = 10000
TEST_ITERATIONS = 5
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "benchmark_test"),
}


class BenchmarkResults:
    def __init__(self, name: str):
        self.name = name
        self.insert_times = []
        self.read_times = []
        self.update_times = []
        self.delete_times = []

    def add_insert_time(self, time_ms: float):
        self.insert_times.append(time_ms)

    def add_read_time(self, time_ms: float):
        self.read_times.append(time_ms)

    def add_update_time(self, time_ms: float):
        self.update_times.append(time_ms)

    def add_delete_time(self, time_ms: float):
        self.delete_times.append(time_ms)

    def get_avg_insert(self) -> float:
        return statistics.mean(self.insert_times) if self.insert_times else 0

    def get_avg_read(self) -> float:
        return statistics.mean(self.read_times) if self.read_times else 0

    def get_avg_update(self) -> float:
        return statistics.mean(self.update_times) if self.update_times else 0

    def get_avg_delete(self) -> float:
        return statistics.mean(self.delete_times) if self.delete_times else 0


@contextmanager
def timer():
    """Context manager to measure execution time"""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    return (end - start) * 1000  # Return milliseconds


def setup_database():
    """Create test database if it doesn't exist"""
    try:
        # Connect to postgres to create database
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="postgres",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname='{DB_CONFIG['database']}'"
        )
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' created")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️  Database setup warning: {e}")


def cleanup_tables():
    """Drop test tables for clean benchmark"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS takeo_benchmark_users CASCADE")
        cursor.execute("DROP TABLE IF EXISTS sqlalchemy_benchmark_users CASCADE")
        conn.commit()
        cursor.close()
        conn.close()
        print("🧹 Test tables cleaned")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")


def benchmark_takeo_orm() -> BenchmarkResults:
    """Benchmark Takeo-ORM performance"""
    print("🚀 Benchmarking Takeo-ORM...")

    try:
        from takeo import Entity, PrimaryGeneratedColumn, Column, createConnection

        @Entity("takeo_benchmark_users")
        class User:
            def __init__(self):
                self.id = None
                self.name = None
                self.email = None
                self.age = None

            id = PrimaryGeneratedColumn()
            name = Column("VARCHAR(100)", nullable=False)
            email = Column("VARCHAR(255)", unique=True)
            age = Column("INTEGER")

            def __str__(self):
                return f"User(id={self.id}, name='{self.name}', email='{self.email}', age={self.age})"

        results = BenchmarkResults("Takeo-ORM")

        # Setup connection ONCE outside the loop
        connection = createConnection(**DB_CONFIG)
        userRepo = connection.getRepository(User)

        for iteration in range(TEST_ITERATIONS):
            print(f"  Iteration {iteration + 1}/{TEST_ITERATIONS}")

            # CREATE TABLE (not timed - setup)
            create_result = connection._api.CreateTable("User")
            if create_result:
                print(f"    Warning: CreateTable returned: {create_result}")

            # 1. INSERT Benchmark
            users = []
            start_time = time.perf_counter()

            for i in range(TEST_RECORDS):
                user = User()
                user.name = f"User_{i}"
                user.email = f"user_{i}@benchmark.com"
                user.age = 20 + (i % 50)
                saved_user = userRepo.save(user)
                users.append(saved_user)

            insert_time = (time.perf_counter() - start_time) * 1000
            results.add_insert_time(insert_time)

            # 2. READ Benchmark
            start_time = time.perf_counter()
            all_users = userRepo.find()
            read_time = (time.perf_counter() - start_time) * 1000
            results.add_read_time(read_time)

            # 3. UPDATE Benchmark
            start_time = time.perf_counter()
            for i in range(0, min(100, len(users))):
                userRepo.update(users[i].id, {"age": 30 + i})
            update_time = (time.perf_counter() - start_time) * 1000
            results.add_update_time(update_time)

            # 4. DELETE Benchmark
            start_time = time.perf_counter()
            for i in range(0, min(100, len(users))):
                userRepo.delete(users[i].id)
            delete_time = (time.perf_counter() - start_time) * 1000
            results.add_delete_time(delete_time)

            # Cleanup for next iteration
            drop_result = connection._api.DropTable("User")
            if drop_result:
                print(f"    Warning: DropTable returned: {drop_result}")

        # Close connection after all iterations
        connection.close()

        return results

    except ImportError:
        print("❌ Takeo-ORM not available. Please build it first with: ./build.sh")
        return BenchmarkResults("Takeo-ORM (Not Available)")
    except Exception as e:
        print(f"❌ Takeo-ORM benchmark error: {e}")
        return BenchmarkResults("Takeo-ORM (Error)")


def benchmark_sqlalchemy() -> BenchmarkResults:
    """Benchmark SQLAlchemy performance"""
    print("🐍 Benchmarking SQLAlchemy...")

    try:
        from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker

        # SQLAlchemy setup
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        Base = declarative_base()

        class User(Base):
            __tablename__ = "sqlalchemy_benchmark_users"

            id = Column(Integer, primary_key=True, autoincrement=True)
            name = Column(String(100), nullable=False)
            email = Column(String(255), unique=True)
            age = Column(Integer)

        results = BenchmarkResults("SQLAlchemy")
        Session = sessionmaker(bind=engine)

        for iteration in range(TEST_ITERATIONS):
            print(f"  Iteration {iteration + 1}/{TEST_ITERATIONS}")

            # CREATE TABLE (not timed - setup)
            Base.metadata.create_all(engine)
            session = Session()

            # 1. INSERT Benchmark
            users = []
            start_time = time.perf_counter()

            for i in range(TEST_RECORDS):
                user = User(
                    name=f"User_{i}", email=f"user_{i}@benchmark.com", age=20 + (i % 50)
                )
                session.add(user)
                users.append(user)

            session.commit()
            insert_time = (time.perf_counter() - start_time) * 1000
            results.add_insert_time(insert_time)

            # 2. READ Benchmark
            start_time = time.perf_counter()
            all_users = session.query(User).all()
            read_time = (time.perf_counter() - start_time) * 1000
            results.add_read_time(read_time)

            # 3. UPDATE Benchmark
            start_time = time.perf_counter()
            for i in range(0, min(100, len(users))):
                users[i].age = 30 + i
            session.commit()
            update_time = (time.perf_counter() - start_time) * 1000
            results.add_update_time(update_time)

            # 4. DELETE Benchmark
            start_time = time.perf_counter()
            for i in range(0, min(100, len(users))):
                session.delete(users[i])
            session.commit()
            delete_time = (time.perf_counter() - start_time) * 1000
            results.add_delete_time(delete_time)

            # Cleanup for next iteration
            session.close()
            Base.metadata.drop_all(engine)

        return results

    except ImportError:
        print(
            "❌ SQLAlchemy not available. Install with: pip install sqlalchemy psycopg2"
        )
        return BenchmarkResults("SQLAlchemy (Not Available)")
    except Exception as e:
        print(f"❌ SQLAlchemy benchmark error: {e}")
        return BenchmarkResults("SQLAlchemy (Error)")


def print_results(
    takeo_results: BenchmarkResults, sqlalchemy_results: BenchmarkResults
):
    """Print beautiful benchmark results"""
    print("\n" + "=" * 80)
    print("🏆 BENCHMARK RESULTS")
    print("=" * 80)

    print(f"\n📊 Test Configuration:")
    print(f"   • Records: {TEST_RECORDS:,}")
    print(f"   • Iterations: {TEST_ITERATIONS}")
    print(f"   • Database: PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']})")

    # Results table
    print(f"\n📈 Performance Comparison (average over {TEST_ITERATIONS} iterations):")
    print("-" * 80)
    print(
        f"{'Operation':<15} {'Takeo-ORM':<15} {'SQLAlchemy':<15} {'Performance Gain':<20}"
    )
    print("-" * 80)

    # INSERT comparison
    takeo_insert = takeo_results.get_avg_insert()
    sqlalchemy_insert = sqlalchemy_results.get_avg_insert()
    insert_gain = (
        f"{sqlalchemy_insert/takeo_insert:.1f}x faster" if takeo_insert > 0 else "N/A"
    )

    print(
        f"{'INSERT':<15} {takeo_insert:>11.1f}ms {sqlalchemy_insert:>11.1f}ms {insert_gain:>15}"
    )

    # READ comparison
    takeo_read = takeo_results.get_avg_read()
    sqlalchemy_read = sqlalchemy_results.get_avg_read()
    read_gain = f"{sqlalchemy_read/takeo_read:.1f}x faster" if takeo_read > 0 else "N/A"

    print(
        f"{'READ':<15} {takeo_read:>11.1f}ms {sqlalchemy_read:>11.1f}ms {read_gain:>15}"
    )

    # UPDATE comparison
    takeo_update = takeo_results.get_avg_update()
    sqlalchemy_update = sqlalchemy_results.get_avg_update()
    update_gain = (
        f"{sqlalchemy_update/takeo_update:.1f}x faster" if takeo_update > 0 else "N/A"
    )

    print(
        f"{'UPDATE':<15} {takeo_update:>11.1f}ms {sqlalchemy_update:>11.1f}ms {update_gain:>15}"
    )

    # DELETE comparison
    takeo_delete = takeo_results.get_avg_delete()
    sqlalchemy_delete = sqlalchemy_results.get_avg_delete()
    delete_gain = (
        f"{sqlalchemy_delete/takeo_delete:.1f}x faster" if takeo_delete > 0 else "N/A"
    )

    print(
        f"{'DELETE':<15} {takeo_delete:>11.1f}ms {sqlalchemy_delete:>11.1f}ms {delete_gain:>15}"
    )

    print("-" * 80)

    # Summary
    if all([takeo_insert, takeo_read, takeo_update, takeo_delete]) > 0:
        avg_takeo = statistics.mean(
            [takeo_insert, takeo_read, takeo_update, takeo_delete]
        )
        avg_sqlalchemy = statistics.mean(
            [sqlalchemy_insert, sqlalchemy_read, sqlalchemy_update, sqlalchemy_delete]
        )
        overall_gain = avg_sqlalchemy / avg_takeo

        print(
            f"\n🎯 Overall Performance: Takeo-ORM is {overall_gain:.1f}x faster than SQLAlchemy"
        )

        if overall_gain >= 20:
            print("🚀 EXCELLENT! Takeo-ORM delivers on its performance promises!")
        elif overall_gain >= 10:
            print("✅ GOOD! Takeo-ORM shows significant performance improvement!")
        elif overall_gain >= 2:
            print("👍 DECENT! Takeo-ORM is faster but room for improvement!")
        else:
            print("⚠️  CONCERNING! Performance claims need verification!")

    print("=" * 80)


def main():
    """Run the complete benchmark"""
    print("🎯 TAKEO-ORM vs SQLAlchemy PERFORMANCE BENCHMARK")
    print("=" * 80)

    # Setup
    print("🔧 Setting up benchmark environment...")
    setup_database()
    cleanup_tables()

    # Run benchmarks
    takeo_results = benchmark_takeo_orm()
    sqlalchemy_results = benchmark_sqlalchemy()

    # Show results
    print_results(takeo_results, sqlalchemy_results)

    # Cleanup
    cleanup_tables()
    print("\n✅ Benchmark completed!")


if __name__ == "__main__":
    main()
