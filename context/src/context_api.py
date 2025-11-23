"""
Context API - High-level interface for loading and saving project state.
"""
from typing import Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from orchestrator.src.models import (
    ProjectState,
    TaskNode,
    AgentResponse,
    Status,
    DeploymentInfo as DeploymentInfoModel,
)
from context.src.schema import Project, Task, AgentHistory, DeploymentInfo
from context.src.database import get_db


def load_project_state(project_id: str, db: Session) -> Optional[ProjectState]:
    """
    Load complete project state from database.

    Args:
        project_id: Project ID to load
        db: Database session

    Returns:
        ProjectState object or None if not found
    """
    # Load project
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        return None

    # Load tasks
    tasks = db.query(Task).filter(Task.project_id == project_id).order_by(Task.created_at).all()
    task_nodes = [
        TaskNode(
            task_id=task.task_id,
            agent=task.agent,
            kind=task.kind,
            description=task.description,
            depends_on=task.depends_on,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]

    # Load agent history
    history = (
        db.query(AgentHistory)
        .filter(AgentHistory.project_id == project_id)
        .order_by(AgentHistory.created_at)
        .all()
    )
    agent_responses = [AgentResponse(**h.response_json) for h in history]

    # Load deployment info
    deployment = db.query(DeploymentInfo).filter(DeploymentInfo.project_id == project_id).first()
    deployment_info = DeploymentInfoModel()
    if deployment:
        deployment_info = DeploymentInfoModel(
            app_url=deployment.app_url,
            deployment_id=deployment.deployment_id,
            status=deployment.status,
        )

    # Construct ProjectState
    return ProjectState(
        project_id=project.project_id,
        user_id=project.user_id,
        goal=project.goal,
        constraints=project.constraints,
        task_graph=task_nodes,
        history=agent_responses,
        deployment_info=deployment_info,
        user_preferences=project.user_preferences,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def save_project_state(state: ProjectState, db: Session) -> None:
    """
    Save complete project state to database.

    Args:
        state: ProjectState to save
        db: Database session
    """
    # Upsert project
    project = db.query(Project).filter(Project.project_id == state.project_id).first()
    if project:
        # Update existing
        project.user_id = state.user_id
        project.goal = state.goal
        project.constraints = state.constraints
        project.user_preferences = state.user_preferences
        project.updated_at = datetime.utcnow()
    else:
        # Create new
        project = Project(
            project_id=state.project_id,
            user_id=state.user_id,
            goal=state.goal,
            constraints=state.constraints,
            user_preferences=state.user_preferences,
        )
        db.add(project)

    # Upsert tasks
    for task_node in state.task_graph:
        task = db.query(Task).filter(Task.task_id == task_node.task_id).first()
        if task:
            # Update existing
            task.agent = task_node.agent
            task.kind = task_node.kind
            task.description = task_node.description
            task.depends_on = task_node.depends_on
            task.status = task_node.status
            task.updated_at = datetime.utcnow()
        else:
            # Create new
            task = Task(
                task_id=task_node.task_id,
                project_id=state.project_id,
                agent=task_node.agent,
                kind=task_node.kind,
                description=task_node.description,
                depends_on=task_node.depends_on,
                status=task_node.status,
            )
            db.add(task)

    # Upsert deployment info
    if state.deployment_info:
        deployment = (
            db.query(DeploymentInfo).filter(DeploymentInfo.project_id == state.project_id).first()
        )
        if deployment:
            # Update existing
            deployment.app_url = state.deployment_info.app_url
            deployment.deployment_id = state.deployment_info.deployment_id
            deployment.status = state.deployment_info.status
            deployment.updated_at = datetime.utcnow()
        else:
            # Create new
            deployment = DeploymentInfo(
                project_id=state.project_id,
                app_url=state.deployment_info.app_url,
                deployment_id=state.deployment_info.deployment_id,
                status=state.deployment_info.status,
            )
            db.add(deployment)

    db.commit()


def append_agent_response(project_id: str, response: AgentResponse, db: Session) -> None:
    """
    Append an agent response to the project history.

    Args:
        project_id: Project ID
        response: AgentResponse to append
        db: Database session
    """
    history_entry = AgentHistory(
        id=str(uuid4()),
        project_id=project_id,
        task_id=response.task_id,
        agent=response.agent,
        status=response.status,
        response_json=response.model_dump(),
    )
    db.add(history_entry)
    db.commit()


def update_task_status(project_id: str, task_id: str, status: Status, db: Session) -> None:
    """
    Update the status of a specific task.

    Args:
        project_id: Project ID
        task_id: Task ID to update
        status: New status
        db: Database session
    """
    task = (
        db.query(Task)
        .filter(Task.project_id == project_id, Task.task_id == task_id)
        .first()
    )
    if task:
        task.status = status
        task.updated_at = datetime.utcnow()
        db.commit()


def update_deployment_info(
    project_id: str,
    app_url: Optional[str] = None,
    deployment_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = None,
) -> None:
    """
    Update deployment information for a project.

    Args:
        project_id: Project ID
        app_url: Application URL
        deployment_id: Deployment ID
        status: Deployment status
        db: Database session
    """
    deployment = (
        db.query(DeploymentInfo).filter(DeploymentInfo.project_id == project_id).first()
    )

    if deployment:
        if app_url is not None:
            deployment.app_url = app_url
        if deployment_id is not None:
            deployment.deployment_id = deployment_id
        if status is not None:
            deployment.status = status
        deployment.updated_at = datetime.utcnow()
    else:
        deployment = DeploymentInfo(
            project_id=project_id,
            app_url=app_url,
            deployment_id=deployment_id,
            status=status,
        )
        db.add(deployment)

    db.commit()
