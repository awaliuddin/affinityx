#!/bin/bash
# Run all tests

set -e

echo "🧪 Running tests for AI Product Studio..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Python tests
echo "Running Python tests..."
pytest -v

echo ""
echo "✅ All tests passed!"
