#!/bin/bash
# Install benchmark dependencies

echo "📦 Installing benchmark dependencies..."

# Install SQLAlchemy and PostgreSQL driver
pip install sqlalchemy psycopg2-binary

echo "✅ Dependencies installed!"
echo ""
echo "🚀 To run the benchmark:"
echo "   1. Make sure PostgreSQL is running"
echo "   2. Set environment variables (or use .env file):"
echo "      export DB_HOST=localhost"
echo "      export DB_USER=postgres" 
echo "      export DB_PASSWORD=your_password"
echo "      export DB_NAME=benchmark_test"
echo "   3. Build Takeo-ORM: ./build.sh"
echo "   4. Run benchmark: python benchmark.py"