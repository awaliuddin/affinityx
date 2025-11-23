"""
Orchestration logic - coordinates task execution across agents.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from orchestrator.src.models import (
    ProjectId,
    ProjectState,
    AgentRequest,
    AgentResponse,
    Status,
    TaskKind,
)
from orchestrator.src.task_graph import get_next_available_task
from context.src.context_api import (
    load_project_state,
    save_project_state,
    append_agent_response,
    update_task_status,
    update_deployment_info,
)


def run_next_available_task(project_id: ProjectId, db: Session, agent_runtime) -> Optional[AgentResponse]:
    """
    Find and execute the next available task for a project.

    Args:
        project_id: Project ID
        db: Database session
        agent_runtime: AgentRuntime instance for executing agents

    Returns:
        AgentResponse from the executed task, or None if no tasks available
    """
    # Load current project state
    state = load_project_state(project_id, db)
    if not state:
        raise ValueError(f"Project {project_id} not found")

    # Find next available task
    try:
        next_task = get_next_available_task(state.task_graph)
    except StopIteration:
        # No more tasks available
        return None

    # Mark task as in progress
    update_task_status(project_id, next_task.task_id, Status.IN_PROGRESS, db)

    # Build AgentRequest
    agent_request = build_agent_request(state, next_task)

    # Execute task via AgentRuntime
    try:
        agent_response = agent_runtime.run(agent_request)

        # Update task status based on response
        update_task_status(project_id, next_task.task_id, agent_response.status, db)

        # Append agent response to history
        append_agent_response(project_id, agent_response, db)

        # Update deployment info if this was a deployment task
        if next_task.kind == TaskKind.DEPLOY_APP and agent_response.result:
            ops_result = agent_response.result
            if "app_url" in ops_result:
                update_deployment_info(
                    project_id=project_id,
                    app_url=ops_result.get("app_url"),
                    deployment_id=ops_result.get("deployment_id"),
                    status=ops_result.get("deployment_status"),
                    db=db,
                )

        return agent_response

    except Exception as e:
        # Mark task as failed
        update_task_status(project_id, next_task.task_id, Status.FAILED, db)

        # Create failure response
        failure_response = AgentResponse(
            project_id=project_id,
            task_id=next_task.task_id,
            agent=next_task.agent,
            status=Status.FAILED,
            logs=f"Task execution failed: {str(e)}",
        )
        append_agent_response(project_id, failure_response, db)

        raise


def build_agent_request(state: ProjectState, task_node) -> AgentRequest:
    """
    Build an AgentRequest from ProjectState and TaskNode.

    Args:
        state: Current project state
        task_node: Task to execute

    Returns:
        AgentRequest ready to be executed
    """
    # Gather relevant context from history
    relevant_context = []
    for response in state.history:
        if response.logs:
            relevant_context.append(f"[{response.agent}] {response.logs[:200]}")

    # Build agent-specific payload based on task kind
    payload = build_task_payload(state, task_node)

    return AgentRequest(
        project_id=state.project_id,
        task_id=task_node.task_id,
        agent=task_node.agent,
        goal=state.goal,
        task_description=task_node.description,
        constraints=state.constraints,
        relevant_context=relevant_context[-5:],  # Last 5 context items
        payload=payload,
    )


def build_task_payload(state: ProjectState, task_node) -> dict:
    """
    Build agent-specific payload for a task.

    Args:
        state: Project state
        task_node: Task node

    Returns:
        Dictionary payload for the agent
    """
    kind = task_node.kind

    if kind == TaskKind.DEFINE_REQUIREMENTS or kind == TaskKind.ARCHITECTURE_AND_STACK:
        return {
            "raw_user_idea": state.goal,
            "existing_requirements": None,
        }

    elif kind == TaskKind.GENERATE_BACKEND_CODE:
        return {
            "architecture_spec": _get_architecture_spec(state),
            "work_scope": "backend",
            "target_paths": [],
        }

    elif kind == TaskKind.GENERATE_FRONTEND_CODE:
        return {
            "architecture_spec": _get_architecture_spec(state),
            "work_scope": "frontend",
            "target_paths": [],
        }

    elif kind == TaskKind.INTEGRATE_AUTH_AND_PERSISTENCE:
        return {
            "architecture_spec": _get_architecture_spec(state),
            "work_scope": "auth_persistence",
            "target_paths": [],
        }

    elif kind == TaskKind.REVIEW_CRITICAL_PATH:
        return {
            "requirements_summary": _get_requirements_summary(state),
            "files_to_review": _get_generated_files(state),
            "run_tests": True,
        }

    elif kind == TaskKind.DEPLOY_APP:
        return {
            "deployment_target": "dev_default",
            "env_config": state.constraints,
            "repo_ref": f"projects/{state.project_id}",
        }

    elif kind == TaskKind.UX_COPY_AND_MICRODETAILS:
        return {
            "user_persona": _infer_user_persona(state),
            "primary_flow": state.goal,
            "front_end_paths": _get_frontend_files(state),
        }

    elif kind == TaskKind.FINAL_SUMMARY:
        return {
            "project_state": state.model_dump(),
        }

    return {}


def _get_architecture_spec(state: ProjectState) -> str:
    """Extract architecture spec from agent history"""
    for response in state.history:
        if "architecture" in str(response.agent).lower():
            for artifact in response.artifacts:
                if artifact.kind == "architecture_spec":
                    return artifact.summary or ""
    return state.goal


def _get_requirements_summary(state: ProjectState) -> str:
    """Extract requirements summary from state"""
    for response in state.history:
        if "architect" in str(response.agent).lower():
            return response.logs[:500]
    return state.goal


def _get_generated_files(state: ProjectState) -> list:
    """Get list of generated files from implementer responses"""
    files = []
    for response in state.history:
        if response.agent == "implementer":
            for artifact in response.artifacts:
                if artifact.kind == "code_file":
                    files.append(artifact.path)
    return files


def _get_frontend_files(state: ProjectState) -> list:
    """Get list of frontend files"""
    files = _get_generated_files(state)
    return [f for f in files if "frontend" in f or "ui" in f]


def _infer_user_persona(state: ProjectState) -> str:
    """Infer user persona from project goal"""
    goal_lower = state.goal.lower()
    if "todo" in goal_lower or "task" in goal_lower:
        return "Busy professional who wants to organize their tasks"
    elif "blog" in goal_lower:
        return "Content creator who wants to publish articles"
    elif "shop" in goal_lower or "store" in goal_lower:
        return "Small business owner who wants to sell online"
    else:
        return "End user who wants a simple, intuitive application"
