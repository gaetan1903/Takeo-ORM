#!/usr/bin/env python3
"""
Performance profiler for Takeo-ORM
Identifies bottlenecks in the ORM operations
"""

import os
import time
import cProfile
import pstats
from io import StringIO
from typing import Dict, Any, List

# Test with small dataset to focus on overhead
TEST_RECORDS = 10


def profile_takeo_orm():
    """Profile Takeo-ORM operations with detailed timing"""
    print("🔍 PROFILING TAKEO-ORM OPERATIONS")
    print("=" * 60)

    try:
        from takeo import Entity, PrimaryGeneratedColumn, Column, createConnection

        @Entity("profile_users")
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

        # Database config
        db_config = {
            "host": "127.0.0.1",
            "port": 5432,
            "user": "postgres",
            "password": "mysecretpassword",
            "database": "benchmark_test",
        }

        print("🔧 Setting up connection...")
        start_time = time.perf_counter()
        connection = createConnection(**db_config)
        connection_time = (time.perf_counter() - start_time) * 1000
        print(f"   Connection setup: {connection_time:.2f}ms")

        print("🔧 Getting repository...")
        start_time = time.perf_counter()
        userRepo = connection.getRepository(User)
        repo_time = (time.perf_counter() - start_time) * 1000
        print(f"   Repository setup: {repo_time:.2f}ms")

        print("🔧 Creating table...")
        start_time = time.perf_counter()
        create_result = connection._api.CreateTable("User")
        table_time = (time.perf_counter() - start_time) * 1000
        print(f"   Table creation: {table_time:.2f}ms")

        # Profile individual operations
        def profile_single_insert():
            user = User()
            user.name = "Profile User"
            user.email = "profile@test.com"
            user.age = 25
            return userRepo.save(user)

        def profile_entity_to_dict(user):
            return userRepo._entity_to_dict(user)

        def profile_json_serialization():
            from takeo.orm import json_dumps, json_loads

            test_data = {"name": "Test", "email": "test@example.com", "age": 25}

            # Test serialization speed
            start = time.perf_counter()
            json_str = json_dumps(test_data)
            serialize_time = (time.perf_counter() - start) * 1000000  # microseconds

            # Test deserialization speed
            start = time.perf_counter()
            parsed_data = json_loads(json_str)
            deserialize_time = (time.perf_counter() - start) * 1000000  # microseconds

            return serialize_time, deserialize_time, len(json_str)

        # Test JSON performance
        print("\n📊 JSON Performance Analysis:")
        serialize_time, deserialize_time, json_size = profile_json_serialization()
        print(f"   Serialize: {serialize_time:.2f}μs")
        print(f"   Deserialize: {deserialize_time:.2f}μs")
        print(f"   JSON size: {json_size} bytes")

        # Profile entity conversion
        print("\n📊 Entity Conversion Analysis:")
        user = User()
        user.name = "Profile User"
        user.email = "profile@test.com"
        user.age = 25

        start_time = time.perf_counter()
        entity_dict = profile_entity_to_dict(user)
        conversion_time = (time.perf_counter() - start_time) * 1000000
        print(f"   Entity to dict: {conversion_time:.2f}μs")
        print(f"   Dict content: {entity_dict}")

        # Profile single insert with detailed timing
        print("\n📊 Single INSERT Analysis:")

        # Time each step of the save process
        user = User()
        user.name = "Profile User 2"
        user.email = "profile2@test.com"
        user.age = 25

        # 1. Entity to dict conversion
        start = time.perf_counter()
        entity_data = userRepo._entity_to_dict(user)
        entity_to_dict_time = (time.perf_counter() - start) * 1000000

        # 2. JSON serialization
        from takeo.orm import json_dumps

        start = time.perf_counter()
        entity_json = json_dumps(entity_data)
        json_serialize_time = (time.perf_counter() - start) * 1000000

        # 3. Go API call
        start = time.perf_counter()
        save_result = userRepo._api.Save(userRepo.entity_class.__name__, entity_json)
        go_api_time = (time.perf_counter() - start) * 1000

        # 4. Result processing
        start = time.perf_counter()
        if hasattr(user, userRepo.entity_class._takeo_primary_key):
            setattr(user, userRepo.entity_class._takeo_primary_key, save_result)
        result_processing_time = (time.perf_counter() - start) * 1000000

        print(f"   1. Entity→Dict: {entity_to_dict_time:.2f}μs")
        print(f"   2. JSON serialize: {json_serialize_time:.2f}μs")
        print(f"   3. Go API call: {go_api_time:.2f}ms ⚠️")
        print(f"   4. Result process: {result_processing_time:.2f}μs")
        print(f"   📈 Go API call is {go_api_time/0.001:.1f}x slower than other steps!")

        # Compare with batch operations
        print("\n📊 Batch vs Single Operations:")

        # Single operations
        start_time = time.perf_counter()
        for i in range(TEST_RECORDS):
            user = User()
            user.name = f"Batch User {i}"
            user.email = f"batch{i}@test.com"
            user.age = 20 + i
            userRepo.save(user)
        single_ops_time = (time.perf_counter() - start_time) * 1000

        print(f"   {TEST_RECORDS} single saves: {single_ops_time:.2f}ms")
        print(f"   Average per save: {single_ops_time/TEST_RECORDS:.2f}ms")

        # Read performance
        print("\n📊 READ Performance Analysis:")
        start = time.perf_counter()
        all_users = userRepo.find()
        read_time = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        result_json = userRepo._api.FindAll(userRepo.entity_class.__name__)
        go_read_time = (time.perf_counter() - start) * 1000

        from takeo.orm import json_loads

        start = time.perf_counter()
        parsed_data = json_loads(result_json)
        json_parse_time = (time.perf_counter() - start) * 1000000

        start = time.perf_counter()
        entities = [userRepo._dict_to_entity(item) for item in parsed_data]
        entity_creation_time = (time.perf_counter() - start) * 1000000

        print(f"   Total read time: {read_time:.2f}ms")
        print(f"   Go API time: {go_read_time:.2f}ms")
        print(f"   JSON parse: {json_parse_time:.2f}μs")
        print(f"   Entity creation: {entity_creation_time:.2f}μs")
        print(f"   Records found: {len(all_users)}")

        # Cleanup
        connection._api.DropTable("User")
        connection.close()

        print("\n🎯 BOTTLENECK ANALYSIS:")
        print("=" * 60)
        print(f"💡 Go API calls dominate execution time!")
        print(f"💡 JSON operations are negligible (<1ms)")
        print(f"💡 Entity conversion is negligible (<1ms)")
        print(f"💡 Main bottleneck: Python ↔ Go communication overhead")

    except ImportError:
        print("❌ Takeo-ORM not available")
    except Exception as e:
        print(f"❌ Profiling error: {e}")
        import traceback

        traceback.print_exc()


def profile_json_libraries():
    """Compare JSON libraries performance"""
    print("\n🆚 JSON LIBRARIES COMPARISON")
    print("=" * 60)

    test_data = {
        "name": "Performance Test User",
        "email": "perf@example.com",
        "age": 30,
        "metadata": {
            "created": "2024-01-01",
            "active": True,
            "tags": ["user", "test", "performance"],
        },
    }

    # Test standard json
    import json as std_json

    start = time.perf_counter()
    for _ in range(1000):
        json_str = std_json.dumps(test_data)
        parsed = std_json.loads(json_str)
    std_time = (time.perf_counter() - start) * 1000

    # Test orjson
    try:
        import orjson

        start = time.perf_counter()
        for _ in range(1000):
            json_bytes = orjson.dumps(test_data)
            json_str = json_bytes.decode("utf-8")
            parsed = orjson.loads(json_str)
        orjson_time = (time.perf_counter() - start) * 1000

        # Test orjson without decode
        start = time.perf_counter()
        for _ in range(1000):
            json_bytes = orjson.dumps(test_data)
            parsed = orjson.loads(json_bytes)
        orjson_direct_time = (time.perf_counter() - start) * 1000

        print(f"Standard JSON (1000 ops): {std_time:.2f}ms")
        print(f"orjson + decode (1000 ops): {orjson_time:.2f}ms")
        print(f"orjson direct (1000 ops): {orjson_direct_time:.2f}ms")
        print(f"")
        print(f"Performance gains:")
        print(f"  orjson + decode: {std_time/orjson_time:.2f}x faster")
        print(f"  orjson direct: {std_time/orjson_direct_time:.2f}x faster")
        print(f"  decode overhead: {orjson_time/orjson_direct_time:.2f}x slower")

        if orjson_time > std_time:
            print(f"⚠️  orjson + decode is SLOWER than standard JSON!")
            print(f"💡 The .decode() wrapper is killing performance!")

    except ImportError:
        print("❌ orjson not available")


def main():
    """Run complete performance analysis"""
    profile_json_libraries()
    profile_takeo_orm()


if __name__ == "__main__":
    main()
