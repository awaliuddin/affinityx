"""
Ops Agent - Handles deployment.
"""
from orchestrator.src.models import (
    AgentRequest,
    AgentResponse,
    OpsResult,
    ArtifactRef,
    Status,
    Suggestion,
)
from tools.deploy import deployer
from tools.repo import file_ops


class OpsAgent:
    """
    Ops Agent deploys applications to target environments.
    """

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute deployment task"""
        deployment_target = request.payload.get("deployment_target", "dev_default")
        env_config = request.payload.get("env_config", {})

        # Generate Docker files if they don't exist
        self._ensure_docker_files(request.project_id)

        # Execute deployment
        deployment_result = deployer.run(deployment_target, env_config)

        ops_result = OpsResult(
            deployment_status=deployment_result["status"],
            deployment_id=deployment_result.get("deployment_id"),
            app_url=deployment_result.get("app_url"),
            logs_excerpt=deployment_result.get("logs_excerpt"),
        )

        return AgentResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            agent=request.agent,
            status=Status.SUCCESS,
            artifacts=[
                ArtifactRef(
                    kind="deployment_info",
                    path="deployment",
                    summary=f"Deployed to {deployment_target}",
                )
            ],
            result=ops_result.model_dump(),
            next_suggestions=[
                Suggestion(
                    title="Improve UX",
                    description="Apply UX improvements to the deployed app",
                )
            ],
            logs=f"Deployment complete. App URL: {ops_result.app_url}",
        )

    def _ensure_docker_files(self, project_id: str):
        """Generate Docker configuration files"""
        # Backend Dockerfile
        backend_dockerfile = '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        file_ops.write("infra/Dockerfile.backend", backend_dockerfile)

        # Frontend Dockerfile
        frontend_dockerfile = '''FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
'''
        file_ops.write("infra/Dockerfile.frontend", frontend_dockerfile)

        # Docker Compose
        docker_compose = '''version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_product_studio
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ../generated/app/backend
      dockerfile: ../../../infra/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/ai_product_studio
    depends_on:
      - postgres

  frontend:
    build:
      context: ../generated/app/frontend
      dockerfile: ../../../infra/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
'''
        file_ops.write("infra/docker-compose.yml", docker_compose)
