"""
Main FastAPI application for the AI Product Studio Orchestrator.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from orchestrator.src.models import (
    CreateProjectRequest,
    CreateProjectResponse,
    GetProjectStatusResponse,
    ProjectState,
    DeploymentInfo,
)
from orchestrator.src.task_graph import create_phase1_task_graph
from orchestrator.src.orchestration import run_next_available_task
from orchestrator.src.agent_runtime import AgentRuntime
from context.src.database import get_db, init_db
from context.src.context_api import load_project_state, save_project_state

# Initialize FastAPI app
app = FastAPI(
    title="AI Product Studio - Orchestrator",
    description="Autonomous AI Product Studio - Transform ideas into live Micro SaaS",
    version="0.1.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent runtime
agent_runtime = AgentRuntime()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Product Studio Orchestrator",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/projects", response_model=CreateProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new project from a user idea.

    This endpoint:
    1. Creates a new ProjectState with a canonical Phase 1 task graph
    2. Persists it to the database
    3. Returns the project ID and task graph
    """
    # Create task graph
    task_graph = create_phase1_task_graph()

    # Create project state
    project = ProjectState(
        user_id=request.user_id,
        goal=request.goal,
        constraints=request.constraints,
        task_graph=task_graph,
        deployment_info=DeploymentInfo(),
    )

    # Save to database
    save_project_state(project, db)

    return CreateProjectResponse(
        project_id=project.project_id,
        task_graph=task_graph,
    )


@app.get("/projects/{project_id}", response_model=GetProjectStatusResponse)
async def get_project_status(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the current status of a project.

    Returns complete project state including:
    - Task graph with current status
    - Agent execution history
    - Deployment information
    """
    project = load_project_state(project_id, db)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return GetProjectStatusResponse(project=project)


@app.post("/projects/{project_id}/step")
async def step_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Execute the next available task for a project (dev mode).

    This endpoint is useful for development and testing.
    In production, tasks would be executed automatically via background workers.
    """
    project = load_project_state(project_id, db)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    try:
        response = run_next_available_task(project_id, db, agent_runtime)

        if response is None:
            return {
                "message": "No more tasks available to execute",
                "project_id": project_id,
            }

        # Reload project to get updated state
        updated_project = load_project_state(project_id, db)

        return {
            "message": "Task executed successfully",
            "project_id": project_id,
            "task_id": response.task_id,
            "agent": response.agent,
            "status": response.status,
            "logs": response.logs,
            "project": updated_project,
        }

    except StopIteration as e:
        return {
            "message": str(e),
            "project_id": project_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Task execution failed: {str(e)}"
        )


@app.post("/projects/{project_id}/execute-all")
async def execute_all_tasks(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Execute all available tasks sequentially (dev mode).

    This is a convenience endpoint for development.
    """
    project = load_project_state(project_id, db)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    executed_tasks = []
    max_iterations = 20  # Safety limit

    for _ in range(max_iterations):
        try:
            response = run_next_available_task(project_id, db, agent_runtime)

            if response is None:
                break

            executed_tasks.append({
                "task_id": response.task_id,
                "agent": response.agent,
                "status": response.status,
            })

        except StopIteration:
            break
        except Exception as e:
            executed_tasks.append({
                "error": str(e),
            })
            break

    # Reload final project state
    final_project = load_project_state(project_id, db)

    return {
        "message": f"Executed {len(executed_tasks)} tasks",
        "project_id": project_id,
        "executed_tasks": executed_tasks,
        "project": final_project,
    }
