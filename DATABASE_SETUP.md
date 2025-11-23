# Database Setup Guide

Complete guide for setting up the PostgreSQL database for AI Product Studio.

## Quick Setup

### Option 1: Automatic (Recommended)

The database is **automatically initialized** when you start the orchestrator:

```bash
# Just start the app - database auto-initializes on first run
uvicorn orchestrator.src.main:app --reload
```

### Option 2: Manual Initialization Script

```bash
# Using the dedicated init script
python scripts/init_db.py
```

### Option 3: Migration Module

```bash
# Using the migration module
python -m context.migrations.apply
```

### Option 4: Docker (Everything Automatic)

```bash
# Docker handles everything including database setup
docker-compose up -d
```

## Prerequisites

### 1. PostgreSQL Installation

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql

# Or use Docker:
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15

# Or use Docker:
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

**Linux:**
```bash
sudo apt-get install postgresql-15

# Or use Docker:
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

### 2. Create Database

**Using psql:**
```bash
psql -U postgres
CREATE DATABASE ai_product_studio;
\q
```

**Using Docker:**
```bash
docker exec -it postgres psql -U postgres -c "CREATE DATABASE ai_product_studio;"
```

**Or let Python create it:**
```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:postgres@localhost/postgres')
with engine.connect() as conn:
    conn.execute("commit")
    conn.execute("CREATE DATABASE ai_product_studio")
```

## Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Database connection
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_product_studio

# For SQLite (development only - not recommended):
# DATABASE_URL=sqlite:///./dev.db
```

### Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

**Examples:**
```bash
# Local PostgreSQL (default)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_product_studio

# Docker PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_product_studio

# Remote PostgreSQL
DATABASE_URL=postgresql://myuser:mypass@myhost.com:5432/ai_product_studio

# With SSL
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## Verification

### Check Database Exists

```bash
# Using psql
psql -U postgres -c "\l" | grep ai_product_studio

# Using Docker
docker exec -it postgres psql -U postgres -c "\l" | grep ai_product_studio
```

### Check Tables Created

```bash
# Using psql
psql -U postgres -d ai_product_studio -c "\dt"

# Should show:
# - projects
# - tasks
# - agent_history
# - deployment_info

# Using Docker
docker exec -it postgres psql -U postgres -d ai_product_studio -c "\dt"
```

### Test Connection from Python

```python
from context.src.database import engine

# Try to connect
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("✅ Connection successful!")
```

## Database Schema

The database contains 4 main tables:

### 1. `projects`
Stores project metadata and configuration.

```sql
CREATE TABLE projects (
    project_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    goal TEXT NOT NULL,
    constraints JSONB NOT NULL DEFAULT '{}',
    user_preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 2. `tasks`
Stores task graph and execution state.

```sql
CREATE TABLE tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(project_id),
    agent VARCHAR(50) NOT NULL,
    kind VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    depends_on JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 3. `agent_history`
Stores complete agent execution history.

```sql
CREATE TABLE agent_history (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL REFERENCES projects(project_id),
    task_id VARCHAR(255) NOT NULL,
    agent VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    response_json JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 4. `deployment_info`
Stores deployment information for each project.

```sql
CREATE TABLE deployment_info (
    project_id VARCHAR(255) PRIMARY KEY REFERENCES projects(project_id),
    app_url VARCHAR(500),
    deployment_id VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## Troubleshooting

### Error: "No module named context.migrations.apply"

**Solution:** The module was missing. Now fixed! Use one of these methods:

```bash
# Method 1: Simple script
python scripts/init_db.py

# Method 2: Migration module (now works!)
python -m context.migrations.apply

# Method 3: Just start the app (auto-init)
uvicorn orchestrator.src.main:app --reload
```

### Error: "could not connect to server"

**Problem:** PostgreSQL is not running.

**Solution:**
```bash
# Check if running
pg_isready

# Start PostgreSQL
# Windows: Start via Services or:
pg_ctl start -D "C:\Program Files\PostgreSQL\15\data"

# Mac:
brew services start postgresql@15

# Linux:
sudo systemctl start postgresql

# Docker:
docker start postgres
# Or:
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

### Error: "database 'ai_product_studio' does not exist"

**Solution:**
```bash
# Create the database
psql -U postgres -c "CREATE DATABASE ai_product_studio;"

# Or with Docker:
docker exec -it postgres psql -U postgres -c "CREATE DATABASE ai_product_studio;"
```

### Error: "password authentication failed"

**Problem:** Wrong credentials in DATABASE_URL.

**Solution:** Check your `.env` file and PostgreSQL configuration:
```bash
# Default PostgreSQL credentials
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_product_studio

# If you set a different password during installation, use that
```

### Error: "port 5432 already in use"

**Problem:** Another PostgreSQL instance is running.

**Solutions:**
```bash
# Option 1: Use the existing PostgreSQL
# Just create the database and use it

# Option 2: Use a different port
DATABASE_URL=postgresql://postgres:postgres@localhost:15432/ai_product_studio

# Option 3: Stop the other instance
# Windows: Services → PostgreSQL → Stop
# Mac: brew services stop postgresql
# Linux: sudo systemctl stop postgresql
```

### Resetting the Database

```bash
# Drop and recreate (loses all data!)
psql -U postgres -c "DROP DATABASE ai_product_studio;"
psql -U postgres -c "CREATE DATABASE ai_product_studio;"

# Then reinitialize
python scripts/init_db.py
```

## Migrations

### Current Migration Files

Located in `context/migrations/`:
- `001_initial_schema.sql` - Initial database schema

### How Migrations Work

1. **Automatic (Recommended):** SQLAlchemy creates tables from Python models
2. **Manual:** SQL files can be applied manually if needed

### Applying Migrations Manually

```bash
# Using psql
psql -U postgres -d ai_product_studio -f context/migrations/001_initial_schema.sql

# Using Docker
docker exec -i postgres psql -U postgres -d ai_product_studio < context/migrations/001_initial_schema.sql
```

## Production Considerations

### 1. Use Connection Pooling

Already configured in `context/src/database.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connections before using
    pool_size=10,        # Number of connections to maintain
    max_overflow=20      # Additional connections if needed
)
```

### 2. Use Environment Variables

Never hardcode database credentials:
```bash
# Good
DATABASE_URL=postgresql://user:pass@host/db

# Bad (never do this)
DATABASE_URL=postgresql://admin:admin123@prodserver/db  # in code
```

### 3. Enable SSL

```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### 4. Regular Backups

```bash
# Backup
pg_dump -U postgres ai_product_studio > backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres ai_product_studio < backup_20240101.sql
```

### 5. Monitor Connections

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'ai_product_studio';

-- Kill idle connections (if needed)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'ai_product_studio'
AND state = 'idle';
```

## FAQ

**Q: Do I need to run migrations manually?**
A: No! The app auto-initializes the database on startup.

**Q: Can I use SQLite instead of PostgreSQL?**
A: Yes for development, but PostgreSQL is recommended for production.

**Q: How do I migrate data from one database to another?**
A: Use `pg_dump` and `pg_restore` or export/import via the API.

**Q: Can I use Docker for PostgreSQL in production?**
A: Yes, but use volumes for data persistence and proper backups.

**Q: What if I need to add new tables later?**
A: Update the SQLAlchemy models and run `init_db()` or create new migration files.
