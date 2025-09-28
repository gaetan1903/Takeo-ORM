# 📊 Takeo-ORM Benchmark

This benchmark script compares **Takeo-ORM** performance against **SQLAlchemy** to verify our performance claims.

## 🚀 Quick Run

```bash
# 1. Install dependencies
./install_benchmark_deps.sh

# 2. Set up environment
export DB_HOST=localhost
export DB_USER=postgres  
export DB_PASSWORD=your_password
export DB_NAME=benchmark_test

# 3. Make sure Takeo-ORM is built
./build.sh

# 4. Run benchmark
python benchmark.py
```

## 📋 What it tests

- **INSERT**: Creating 1,000 records
- **READ**: Querying all records  
- **UPDATE**: Modifying 100 records
- **DELETE**: Removing 100 records

Each test runs **5 iterations** and shows average performance.

## 🎯 Expected Results

Based on our claims, Takeo-ORM should be **20-30x faster** than SQLAlchemy for most operations.

## 📊 Sample Output

```
🏆 BENCHMARK RESULTS
================================================================================
📊 Test Configuration:
   • Records: 1,000
   • Iterations: 5
   • Database: PostgreSQL (localhost:5432)

📈 Performance Comparison (average over 5 iterations):
--------------------------------------------------------------------------------
Operation       Takeo-ORM       SQLAlchemy      Performance Gain    
--------------------------------------------------------------------------------
INSERT               50.2ms         1,234.5ms         24.6x faster
READ                 28.1ms           892.3ms         31.8x faster  
UPDATE               15.7ms           456.2ms         29.1x faster
DELETE               12.3ms           398.7ms         32.4x faster
--------------------------------------------------------------------------------

🎯 Overall Performance: Takeo-ORM is 29.5x faster than SQLAlchemy
🚀 EXCELLENT! Takeo-ORM delivers on its performance promises!
```

## ⚙️ Configuration

You can customize the benchmark by editing `benchmark.py`:

- `TEST_RECORDS`: Number of records to create (default: 1,000)
- `TEST_ITERATIONS`: Number of test runs (default: 5)
- Database connection via environment variables