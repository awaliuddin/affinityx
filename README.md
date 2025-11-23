# AI Product Studio

**Autonomous AI Product Studio** - Transform ideas into live Micro SaaS applications with multi-agent orchestration.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

## 🚀 Overview

The AI Product Studio accepts a natural language product idea and runs a coordinated multi-agent pipeline to produce a fully deployed micro SaaS web app. Features include:

- 🤖 **6 Specialized AI Agents** working in harmony
- 🔄 **Real-time Workflow Visualization** via WebSocket
- 🎯 **Multi-LLM Support** (OpenAI, Claude, Ollama, Mock)
- 🐳 **Complete Docker Infrastructure** for one-command deployment
- ⚡ **Live Progress Tracking** with beautiful animated UI
- 🎨 **Production-Ready Code** generation

## ✨ New Features

### 🔄 Real-Time Workflow Visualization
- **WebSocket-powered live updates** - Watch agents execute in real-time
- **Animated agent status cards** - Visual feedback for all 6 agents
- **Live activity feed** - See what's happening as it happens
- **Beautiful UI** - Gradient effects, pulse animations, auto-scrolling

### 🤖 Multi-LLM Provider Support
- **OpenAI** - GPT-4, GPT-3.5 Turbo
- **Claude** - Claude 3 (Opus, Sonnet, Haiku)
- **Ollama** - Local models (Llama2, Mistral, CodeLlama, etc.)
- **Mock** - Testing without API calls
- **Per-Agent Configuration** - Use different models for each agent
- **Hot-Swappable** - Change providers without restarting

### 🐳 Complete Docker Infrastructure
- **One-command deployment** - `docker-compose up -d`
- **Multi-stage builds** - Optimized images
- **Health checks** - Robust service management
- **Persistent volumes** - Data survives restarts
- **Network isolation** - Secure service communication

## 🏗️ Architecture

### Multi-Agent System

1. **🎭 Orchestrator** - Coordinates task execution and manages workflow
2. **🏛️ Architect Agent** - Translates ideas into concrete architecture specs
3. **⚙️ Implementer Agent** - Generates full-stack code (FastAPI + React)
4. **🔍 Reviewer Agent** - Quality assurance and security checks
5. **🚢 Ops Agent** - Automated deployment and infrastructure
6. **✨ UX Muse Agent** - UX improvements and microcopy optimization

### Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 with Vite (TypeScript)
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Real-time**: WebSocket for live updates
- **LLM**: OpenAI, Claude, Ollama (configurable)
- **Deployment**: Docker & Docker Compose
- **Testing**: pytest (backend), Vitest (frontend)

## 📦 Quick Start

### Option 1: Docker (Recommended) 🐳

**Simplest way to get started:**

```bash
# Clone the repository
git clone <your-repo-url>
cd affinityx

# Start everything with one command
docker-compose up -d

# That's it! Open your browser
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# WebSocket: ws://localhost:8000/ws/{project_id}
```

**With Local LLM (Ollama):**

```bash
# Start with Ollama included
docker-compose --profile ollama up -d

# Pull a model
docker exec -it ai-studio-ollama ollama pull llama2

# Configure to use Ollama
echo "LLM_PROVIDER=ollama" > .env
echo "LLM_MODEL=llama2" >> .env
docker-compose restart orchestrator
```

**With OpenAI or Claude:**

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# OR for Claude:
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Start services
docker-compose up -d
```

### Option 2: Local Development 💻

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or use Docker)

**Installation:**

```bash
# 1. Install Python dependencies
pip install -e .

# 2. Install UI dependencies
cd ui && npm install && cd ..

# 3. Setup PostgreSQL (choose one method)

# Method A: Using Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15

# Method B: Local PostgreSQL
# Start PostgreSQL service and create database
psql -U postgres -c "CREATE DATABASE ai_product_studio;"

# 4. Initialize database (choose one)
python scripts/init_db.py
# OR
python -m context.migrations.apply
# OR just start the app (auto-initializes)

# 5. Configure environment (optional)
cp .env.example .env
# Edit .env to set LLM provider and API keys

# 6. Start backend
uvicorn orchestrator.src.main:app --reload

# 7. Start frontend (in another terminal)
cd ui && npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🎯 Usage

### Creating Your First App

1. **Open the UI** at http://localhost:5173

2. **Enter your idea**:
   ```
   "Build a simple todo list app with user authentication"
   ```

3. **Watch the magic**:
   - 🏛️ Architect designs the system
   - ⚙️ Implementer generates code
   - 🔍 Reviewer checks quality
   - 🚢 Ops deploys the app
   - ✨ UX Muse polishes the experience

4. **Get your app**:
   - Receive a live URL
   - Full source code generated
   - Database schema created
   - Ready to use!

### Viewing Real-Time Workflow

The UI shows:
- **Agent Status Cards** - See which agent is currently working
- **Live Activity Feed** - Real-time messages from agents
- **Progress Bar** - Track completion percentage
- **Task Timeline** - Detailed task-by-task breakdown

## 🤖 LLM Configuration

### Supported Providers

| Provider | Models | Cost | Speed | Best For |
|----------|--------|------|-------|----------|
| **OpenAI** | GPT-4, GPT-3.5 | $$$ | Fast | Code generation |
| **Claude** | Opus, Sonnet, Haiku | $$ | Fast | Architecture, reasoning |
| **Ollama** | Llama2, Mistral, etc. | Free | Medium | Local development |
| **Mock** | N/A | Free | Instant | Testing |

### Global Configuration

Set one provider for all agents:

```bash
# .env file
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
OPENAI_API_KEY=sk-your-key-here
```

### Per-Agent Configuration (Advanced)

Use different models for each agent to optimize cost/performance:

```bash
# Use Claude for architecture (best reasoning)
ARCHITECT_LLM_PROVIDER=claude
ARCHITECT_LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=sk-ant-xxx

# Use GPT-4 for code generation (best at coding)
IMPLEMENTER_LLM_PROVIDER=openai
IMPLEMENTER_LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-xxx

# Use local Llama2 for reviews (free!)
REVIEWER_LLM_PROVIDER=ollama
REVIEWER_LLM_MODEL=llama2
OLLAMA_API_BASE=http://localhost:11434
```

### Check Provider Status

```bash
# Via API
curl http://localhost:8000/llm/providers

# Response shows which providers are available
{
  "providers": [
    {"provider": "openai", "status": "available"},
    {"provider": "claude", "status": "unavailable", "config_needed": ["ANTHROPIC_API_KEY"]},
    {"provider": "ollama", "status": "available"},
    {"provider": "mock", "status": "available"}
  ],
  "current": "openai"
}
```

## 📡 API Endpoints

### REST API

- **POST** `/projects` - Create a new project
- **GET** `/projects/{project_id}` - Get project status
- **POST** `/projects/{project_id}/step` - Execute next task (dev mode)
- **POST** `/projects/{project_id}/execute-all` - Execute all tasks
- **GET** `/llm/providers` - List available LLM providers
- **GET** `/health` - Health check

### WebSocket API

- **WS** `/ws/{project_id}` - Real-time project updates

**WebSocket Events:**
```javascript
{
  "type": "agent_start",
  "task_id": "task_123",
  "agent": "architect",
  "task_kind": "ARCHITECTURE_AND_STACK"
}

{
  "type": "agent_complete",
  "task_id": "task_123",
  "agent": "architect",
  "status": "success",
  "result": {...}
}

{
  "type": "project_update",
  "project": {...}
}
```

### API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
affinityx/
├── orchestrator/              # Main orchestration service
│   ├── src/
│   │   ├── main.py           # FastAPI application
│   │   ├── models.py         # Pydantic models
│   │   ├── task_graph.py     # Task dependency management
│   │   ├── orchestration.py  # Orchestration logic
│   │   ├── agent_runtime.py  # Agent execution
│   │   ├── websocket_manager.py  # WebSocket handling
│   │   └── llm/              # LLM abstraction layer
│   │       ├── base.py
│   │       ├── openai_provider.py
│   │       ├── claude_provider.py
│   │       ├── ollama_provider.py
│   │       └── factory.py
│   └── tests/
├── agents/                    # AI agent implementations
│   ├── architect/            # Architecture design
│   ├── implementer/          # Code generation
│   ├── reviewer/             # Quality checks
│   ├── ops/                  # Deployment
│   └── ux_muse/             # UX improvements
├── context/                   # Database & persistence
│   ├── src/
│   │   ├── database.py       # SQLAlchemy setup
│   │   ├── schema.py         # Database models
│   │   ├── context_api.py    # State management
│   │   └── vector_store.py   # Vector search
│   └── migrations/
│       └── 001_initial_schema.sql
├── tools/                     # Utility tools
│   ├── repo/                 # File operations
│   ├── tests/                # Test runners
│   └── deploy/               # Deployment tools
├── ui/                        # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   │       ├── CreateProject.tsx
│   │       ├── ProjectProgress.tsx
│   │       └── WorkflowVisualization.tsx
│   ├── package.json
│   └── vite.config.ts
├── generated/                 # AI-generated apps
│   ├── artifacts/            # Architecture specs
│   └── app/                  # Generated code
├── scripts/                   # Utility scripts
│   ├── init_db.py           # Database initialization
│   ├── run_dev.sh           # Development startup
│   └── test.sh              # Run tests
├── Dockerfile.orchestrator   # Backend Docker image
├── Dockerfile.ui             # Frontend Docker image
├── docker-compose.yml        # Full stack deployment
├── pyproject.toml           # Python dependencies
├── .env.example             # Environment template
├── DATABASE_SETUP.md        # Database guide
├── DOCKER.md                # Docker guide
└── README.md                # This file
```

## 🧪 Development

### Running Tests

```bash
# All Python tests
pytest

# With coverage
pytest --cov

# Specific test file
pytest orchestrator/tests/test_models.py

# Frontend tests
cd ui && npm test
```

### Adding a New Agent

1. Create agent directory:
   ```bash
   mkdir -p agents/my_agent
   touch agents/my_agent/__init__.py
   touch agents/my_agent/agent.py
   ```

2. Implement the agent:
   ```python
   from orchestrator.src.models import AgentRequest, AgentResponse, Status

   class MyAgent:
       def execute(self, request: AgentRequest) -> AgentResponse:
           # Your agent logic here
           return AgentResponse(
               project_id=request.project_id,
               task_id=request.task_id,
               agent=request.agent,
               status=Status.SUCCESS,
               result={"message": "Task completed"}
           )
   ```

3. Register in `AgentRuntime`:
   ```python
   # orchestrator/src/agent_runtime.py
   from agents.my_agent.agent import MyAgent

   self.agents = {
       AgentType.MY_AGENT: MyAgent(),
       # ... other agents
   }
   ```

4. Add to task graph if needed

### Code Style

```bash
# Format code
black .

# Lint
ruff check .

# Type checking
mypy orchestrator/
```

## 🚀 Deployment

### Docker Deployment (Production)

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Scale orchestrator
docker-compose up -d --scale orchestrator=3

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Environment Variables

**Required:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
LLM_PROVIDER=openai|claude|ollama|mock
```

**Optional:**
```bash
LLM_MODEL=model-name
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
OLLAMA_API_BASE=http://localhost:11434
SQL_ECHO=false
```

**Agent-Specific:**
```bash
ARCHITECT_LLM_PROVIDER=claude
IMPLEMENTER_LLM_PROVIDER=openai
REVIEWER_LLM_PROVIDER=ollama
```

See [DOCKER.md](DOCKER.md) for complete deployment guide.

## 📚 Documentation

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Database configuration guide
- [DOCKER.md](DOCKER.md) - Docker deployment guide
- [API Docs](http://localhost:8000/docs) - Interactive API documentation

## 🎯 Features

### ✅ Phase 1 Complete
- ✅ Natural language idea input
- ✅ Automated architecture design
- ✅ Full-stack code generation (FastAPI + React)
- ✅ Authentication & persistence integration
- ✅ Code review and quality checks
- ✅ Automated deployment
- ✅ UX copy and improvements
- ✅ **Real-time workflow visualization**
- ✅ **Multi-LLM support (OpenAI, Claude, Ollama)**
- ✅ **Complete Docker infrastructure**
- ✅ **WebSocket live updates**
- ✅ **Per-agent LLM configuration**

### 🔮 Future Enhancements
- [ ] Cloud deployment (AWS, GCP, Azure)
- [ ] Advanced AI models integration
- [ ] Template marketplace
- [ ] Multi-user collaboration
- [ ] CI/CD pipeline generation
- [ ] GitHub integration
- [ ] Advanced monitoring & analytics
- [ ] Custom agent plugins

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [OpenAI](https://openai.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [Ollama](https://ollama.ai/)

---

**Transform your ideas into reality with AI Product Studio!** 🚀✨
