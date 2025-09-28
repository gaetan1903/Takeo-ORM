#!/usr/bin/env python3
"""
Quick benchmark to test batch operations optimization
"""

import os
import time
from typing import List


def benchmark_batch_operations():
    """Test batch vs individual operations"""
    print("🚀 TESTING BATCH OPTIMIZATIONS")
    print("=" * 50)

    try:
        from takeo import Entity, PrimaryGeneratedColumn, Column, createConnection

        @Entity("batch_test_users")
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

        # Setup
        db_config = {
            "host": "127.0.0.1",
            "port": 5432,
            "user": "postgres",
            "password": "mysecretpassword",
            "database": "benchmark_test",
        }

        connection = createConnection(**db_config)
        userRepo = connection.getRepository(User)
        connection._api.CreateTable("User")

        # Create test data
        TEST_SIZE = 50
        users = []
        for i in range(TEST_SIZE):
            user = User()
            user.name = f"Batch User {i}"
            user.email = f"batch{i}@test.com"
            user.age = 20 + (i % 50)
            users.append(user)

        print(f"📊 Testing with {TEST_SIZE} records...")

        # Test individual saves
        individual_users = [User() for _ in range(TEST_SIZE)]
        for i, user in enumerate(individual_users):
            user.name = f"Individual User {i}"
            user.email = f"individual{i}@test.com"
            user.age = 25 + i

        start_time = time.perf_counter()
        for user in individual_users:
            userRepo.save(user)
        individual_time = (time.perf_counter() - start_time) * 1000

        # Test batch saves (if available)
        start_time = time.perf_counter()
        try:
            saved_users = userRepo.saveBatch(users)
            batch_time = (time.perf_counter() - start_time) * 1000
            batch_available = True
        except Exception as e:
            print(f"   Batch not available: {e}")
            batch_time = float("inf")
            batch_available = False

        # Results
        print(f"\n📈 RESULTS:")
        print(
            f"   Individual saves: {individual_time:.2f}ms ({individual_time/TEST_SIZE:.2f}ms per record)"
        )

        if batch_available:
            print(
                f"   Batch save: {batch_time:.2f}ms ({batch_time/TEST_SIZE:.2f}ms per record)"
            )
            improvement = individual_time / batch_time
            print(f"   Improvement: {improvement:.2f}x faster")
        else:
            print(f"   Batch save: Not available (fallback to individual)")

        # Test reads
        start_time = time.perf_counter()
        all_users = userRepo.find()
        read_time = (time.perf_counter() - start_time) * 1000
        print(f"   Read all ({len(all_users)} records): {read_time:.2f}ms")

        # Cleanup
        connection._api.DropTable("User")
        connection.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    benchmark_batch_operations()
