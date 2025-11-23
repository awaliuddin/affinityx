#!/bin/bash
# Development startup script

set -e

echo "🚀 Starting AI Product Studio in development mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q -e .

# Start PostgreSQL with Docker if not running
if ! docker ps | grep -q postgres; then
    echo "Starting PostgreSQL..."
    docker run -d \
        --name ai-studio-postgres \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=ai_product_studio \
        -p 5432:5432 \
        postgres:15 2>/dev/null || docker start ai-studio-postgres
    sleep 3
fi

# Initialize database
echo "Initializing database..."
python -c "from context.src.database import init_db; init_db()"

# Start backend in background
echo "Starting FastAPI backend..."
uvicorn orchestrator.src.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Install frontend dependencies if needed
if [ ! -d "ui/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd ui && npm install && cd ..
fi

# Start frontend
echo "Starting React frontend..."
cd ui && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ AI Product Studio is running!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
