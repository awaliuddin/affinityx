# Docker Deployment Guide

Complete guide for deploying AI Product Studio with Docker.

## Quick Start

### Option 1: Default Setup (Mock LLM)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: With Ollama (Local LLM)

```bash
# Start with Ollama included
docker-compose --profile ollama up -d

# Pull a model (first time only)
docker exec -it ai-studio-ollama ollama pull llama2

# Set environment variable
echo "LLM_PROVIDER=ollama" > .env
echo "LLM_MODEL=llama2" >> .env

# Restart orchestrator
docker-compose restart orchestrator
```

### Option 3: With OpenAI or Claude

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here

# OR for Claude:
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your-api-key-here

# Start services
docker-compose up -d
```

## Architecture

The Docker setup includes:

- **PostgreSQL**: Database for project state and history
- **Orchestrator**: FastAPI backend with all 6 agents
- **UI**: React frontend with workflow visualization
- **Ollama** (optional): Local LLM server

## Services

### PostgreSQL
- **Port**: 5432
- **Database**: ai_product_studio
- **User**: postgres
- **Password**: postgres
- **Volume**: `postgres_data`

### Orchestrator
- **Port**: 8000
- **Health Check**: `/health`
- **WebSocket**: `/ws/{project_id}`
- **API Docs**: `/docs`

### UI
- **Port**: 5173
- **Built with**: Vite + React
- **Serves**: Static files

### Ollama (Optional)
- **Port**: 11434
- **Volume**: `ollama_data`
- **Profile**: `ollama`

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `LLM_PROVIDER`: `openai`, `claude`, `ollama`, or `mock`

### Optional LLM Configuration
- `LLM_MODEL`: Model name (provider-specific)
- `LLM_TEMPERATURE`: 0.0-1.0 (default: 0.7)
- `LLM_MAX_TOKENS`: Max tokens to generate (default: 2000)

### Provider-Specific
- `OPENAI_API_KEY`: For OpenAI models
- `ANTHROPIC_API_KEY`: For Claude models
- `OLLAMA_API_BASE`: Ollama server URL (default: http://ollama:11434)

### Agent-Specific (Advanced)
Override LLM settings per agent:
```bash
ARCHITECT_LLM_PROVIDER=claude
ARCHITECT_LLM_MODEL=claude-3-sonnet-20240229
IMPLEMENTER_LLM_PROVIDER=openai
IMPLEMENTER_LLM_MODEL=gpt-4-turbo-preview
```

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f ui
docker-compose logs -f postgres
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart orchestrator
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# Rebuild specific service
docker-compose build orchestrator
docker-compose up -d orchestrator

# Rebuild all
docker-compose build
docker-compose up -d
```

### Access Container Shell
```bash
# Orchestrator
docker exec -it ai-studio-orchestrator bash

# Postgres
docker exec -it ai-studio-postgres psql -U postgres -d ai_product_studio
```

## Database Management

### Initialize Database
Database is auto-initialized on first start using migrations in `context/migrations/`.

### Manual Migration
```bash
docker exec -it ai-studio-orchestrator python -c "from context.src.database import init_db; init_db()"
```

### Backup Database
```bash
docker exec ai-studio-postgres pg_dump -U postgres ai_product_studio > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker exec -i ai-studio-postgres psql -U postgres ai_product_studio
```

## Troubleshooting

### Port Already in Use
If ports 5432, 8000, or 5173 are in use:
```bash
# Change ports in docker-compose.yml
ports:
  - "15432:5432"  # PostgreSQL
  - "18000:8000"  # Orchestrator
  - "15173:5173"  # UI
```

### Ollama Not Working
```bash
# Check Ollama status
docker exec -it ai-studio-ollama ollama list

# Test Ollama
curl http://localhost:11434/api/tags

# Pull a model
docker exec -it ai-studio-ollama ollama pull llama2
```

### Database Connection Issues
```bash
# Check database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify connection
docker exec -it ai-studio-orchestrator python -c "from context.src.database import engine; print(engine.connect())"
```

### Frontend Can't Connect to Backend
```bash
# Check orchestrator health
curl http://localhost:8000/health

# Check CORS settings in orchestrator/src/main.py
# Ensure your frontend URL is in allow_origins
```

## Production Deployment

### Security Hardening
1. **Change default passwords**:
   ```yaml
   environment:
     POSTGRES_PASSWORD: use-a-strong-password
   ```

2. **Use secrets management**:
   ```bash
   # Use Docker secrets instead of environment variables
   echo "your-api-key" | docker secret create openai_key -
   ```

3. **Enable HTTPS**:
   - Add nginx reverse proxy
   - Configure SSL certificates
   - Update CORS settings

### Scaling
```bash
# Scale orchestrator instances
docker-compose up -d --scale orchestrator=3

# Use load balancer (nginx/traefik)
# Add health checks to load balancer config
```

### Monitoring
```bash
# Add Prometheus + Grafana
# Monitor container metrics
docker stats

# Check health endpoints
curl http://localhost:8000/health
```

## Development Workflow

### Local Development with Docker
```bash
# Mount code as volume for live reload
docker-compose -f docker-compose.dev.yml up
```

### Run Tests in Container
```bash
docker exec -it ai-studio-orchestrator pytest
```

### Debug Container
```bash
# Run with debug mode
docker-compose up

# Attach to running container
docker attach ai-studio-orchestrator
```

## Advanced Configuration

### Custom Network
```yaml
networks:
  ai-studio-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

### Resource Limits
```yaml
services:
  orchestrator:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Persistent Volumes
```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/postgres/data
```

## FAQ

**Q: How do I use a different LLM provider?**
A: Set `LLM_PROVIDER` environment variable and provide the necessary API key.

**Q: Can I run this without Docker?**
A: Yes, see the main README.md for manual installation instructions.

**Q: How do I update to the latest version?**
A: Pull latest code, rebuild containers: `docker-compose build && docker-compose up -d`

**Q: Is Ollama required?**
A: No, Ollama is optional. Use `mock` provider for testing without any LLM.

**Q: How do I monitor agent execution in real-time?**
A: Connect to WebSocket endpoint `/ws/{project_id}` or view the UI workflow visualization.
