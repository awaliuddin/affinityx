# AI Product Studio

**Autonomous AI Product Studio** - Transform ideas into live Micro SaaS applications with multi-agent orchestration.

## Overview

The AI Product Studio accepts a natural language product idea and runs a coordinated multi-agent pipeline to produce a deployed micro SaaS web app. It exposes a simple web UI that shows agent progress and the final app URL.

## Architecture

### Multi-Agent System

- **Orchestrator**: Coordinates task execution across all agents
- **Architect Agent**: Translates ideas into concrete architecture specs
- **Implementer Agent**: Generates backend and frontend code
- **Reviewer Agent**: Provides quality and safety gates
- **Ops Agent**: Deploys applications to development environment
- **UX Muse Agent**: Improves UX text and interaction details

### Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with Vite (TypeScript)
- **Database**: PostgreSQL with pgvector
- **Deployment**: Docker & Docker Compose
- **Testing**: pytest (backend), Vitest (frontend)

## Project Structure

```
ai-product-studio/
├── orchestrator/       # Main orchestration service
│   ├── src/
│   └── tests/
├── agents/             # Specialized AI agents
│   ├── architect/
│   ├── implementer/
│   ├── reviewer/
│   ├── ops/
│   └── ux_muse/
├── context/            # Persistence and context management
│   ├── src/
│   └── migrations/
├── tools/              # Utility tools
│   ├── repo/
│   ├── deploy/
│   └── tests/
├── ui/                 # React frontend
│   ├── src/
│   └── public/
├── infra/              # Docker and infrastructure
└── generated/          # AI-generated applications
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### Installation

```bash
# Install Python dependencies
pip install -e .

# Install UI dependencies
cd ui && npm install

# Setup database
docker-compose up -d postgres
python -m context.migrations.apply

# Start backend
uvicorn orchestrator.src.main:app --reload

# Start frontend (in another terminal)
cd ui && npm run dev
```

### Usage

1. Open http://localhost:5173 in your browser
2. Enter your micro SaaS idea in the textarea
3. Click "Create with AI Team"
4. Watch the multi-agent system build your app!
5. Access your deployed app via the provided URL

## API Endpoints

### Orchestrator API

- `POST /projects` - Create a new project from an idea
- `GET /projects/{project_id}` - Get project status and progress
- `POST /projects/{project_id}/step` - Execute next available task (dev mode)

## Development

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd ui && npm test
```

### Adding a New Agent

1. Create agent directory in `agents/`
2. Implement agent class with `AgentRequest` → `AgentResponse` interface
3. Register agent in `AgentRuntime`
4. Add tasks to orchestrator task graph

## Phase 1 MVP Features

- ✅ Natural language idea input
- ✅ Automated architecture design
- ✅ Backend code generation (FastAPI)
- ✅ Frontend code generation (React)
- ✅ Authentication & persistence integration
- ✅ Code review and quality checks
- ✅ Automated deployment to dev environment
- ✅ UX copy and micro-improvements
- ✅ Real-time progress visualization
- ✅ Live app URL delivery

## License

MIT License
