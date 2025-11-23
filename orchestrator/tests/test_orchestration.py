"""
End-to-end tests for orchestration.
"""
import pytest
from orchestrator.src.models import (
    CreateProjectRequest,
    AgentType,
    TaskKind,
    Status,
)
from orchestrator.src.task_graph import create_phase1_task_graph, get_next_available_task


def test_create_phase1_task_graph():
    """Test that Phase 1 task graph is created correctly"""
    task_graph = create_phase1_task_graph()

    # Should have 9 tasks
    assert len(task_graph) == 9

    # First task should be DEFINE_REQUIREMENTS with no dependencies
    first_task = task_graph[0]
    assert first_task.kind == TaskKind.DEFINE_REQUIREMENTS
    assert first_task.agent == AgentType.ARCHITECT
    assert len(first_task.depends_on) == 0
    assert first_task.status == Status.PENDING

    # Last task should be FINAL_SUMMARY
    last_task = task_graph[-1]
    assert last_task.kind == TaskKind.FINAL_SUMMARY
    assert last_task.agent == AgentType.ORCHESTRATOR

    # Review task should depend on 3 code generation tasks
    review_task = next(t for t in task_graph if t.kind == TaskKind.REVIEW_CRITICAL_PATH)
    assert len(review_task.depends_on) == 3

    # All task IDs should be unique
    task_ids = [t.task_id for t in task_graph]
    assert len(task_ids) == len(set(task_ids))


def test_get_next_available_task():
    """Test task dependency resolution"""
    task_graph = create_phase1_task_graph()

    # First available task should be DEFINE_REQUIREMENTS
    next_task = get_next_available_task(task_graph)
    assert next_task.kind == TaskKind.DEFINE_REQUIREMENTS

    # Mark first task as success and get next
    task_graph[0].status = Status.SUCCESS
    next_task = get_next_available_task(task_graph)
    assert next_task.kind == TaskKind.ARCHITECTURE_AND_STACK

    # Mark architecture task as success
    arch_task = next(t for t in task_graph if t.kind == TaskKind.ARCHITECTURE_AND_STACK)
    arch_task.status = Status.SUCCESS

    # Now multiple tasks should be available (code generation tasks)
    next_task = get_next_available_task(task_graph)
    assert next_task.kind in [
        TaskKind.GENERATE_BACKEND_CODE,
        TaskKind.GENERATE_FRONTEND_CODE,
        TaskKind.INTEGRATE_AUTH_AND_PERSISTENCE,
    ]


def test_create_project_request():
    """Test CreateProjectRequest validation"""
    request = CreateProjectRequest(
        user_id="test_user",
        goal="Build a todo list app",
        constraints={"auth_required": True},
    )

    assert request.user_id == "test_user"
    assert request.goal == "Build a todo list app"
    assert request.constraints["auth_required"] is True


def test_no_available_tasks():
    """Test that StopIteration is raised when no tasks are available"""
    task_graph = create_phase1_task_graph()

    # Mark all tasks as in_progress (none available)
    for task in task_graph:
        task.status = Status.IN_PROGRESS

    with pytest.raises(StopIteration):
        get_next_available_task(task_graph)
