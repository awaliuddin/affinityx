"""
Task graph creation and management.
Creates the canonical Phase 1 task graph with proper dependencies.
"""
from typing import List
from orchestrator.src.models import (
    TaskNode,
    AgentType,
    TaskKind,
    Status,
)


def create_phase1_task_graph() -> List[TaskNode]:
    """
    Create the canonical Phase 1 task graph with all dependencies.

    Returns:
        List of TaskNode objects representing the complete execution pipeline
    """

    # Task 1: Define requirements
    task_1 = TaskNode(
        agent=AgentType.ARCHITECT,
        kind=TaskKind.DEFINE_REQUIREMENTS,
        description="Define requirements from user idea",
        depends_on=[],
        status=Status.PENDING
    )

    # Task 2: Architecture and stack (depends on requirements)
    task_2 = TaskNode(
        agent=AgentType.ARCHITECT,
        kind=TaskKind.ARCHITECTURE_AND_STACK,
        description="Design architecture and select technology stack",
        depends_on=[task_1.task_id],
        status=Status.PENDING
    )

    # Task 3: Generate backend code (depends on architecture)
    task_3 = TaskNode(
        agent=AgentType.IMPLEMENTER,
        kind=TaskKind.GENERATE_BACKEND_CODE,
        description="Generate FastAPI backend code",
        depends_on=[task_2.task_id],
        status=Status.PENDING
    )

    # Task 4: Generate frontend code (depends on architecture)
    task_4 = TaskNode(
        agent=AgentType.IMPLEMENTER,
        kind=TaskKind.GENERATE_FRONTEND_CODE,
        description="Generate React frontend code",
        depends_on=[task_2.task_id],
        status=Status.PENDING
    )

    # Task 5: Integrate auth and persistence (depends on architecture)
    task_5 = TaskNode(
        agent=AgentType.IMPLEMENTER,
        kind=TaskKind.INTEGRATE_AUTH_AND_PERSISTENCE,
        description="Integrate authentication and data persistence",
        depends_on=[task_2.task_id],
        status=Status.PENDING
    )

    # Task 6: Review critical path (depends on all code generation)
    task_6 = TaskNode(
        agent=AgentType.REVIEWER,
        kind=TaskKind.REVIEW_CRITICAL_PATH,
        description="Review generated code for quality and security",
        depends_on=[task_3.task_id, task_4.task_id, task_5.task_id],
        status=Status.PENDING
    )

    # Task 7: Deploy app (depends on review passing)
    task_7 = TaskNode(
        agent=AgentType.OPS,
        kind=TaskKind.DEPLOY_APP,
        description="Deploy application to development environment",
        depends_on=[task_6.task_id],
        status=Status.PENDING
    )

    # Task 8: UX improvements (depends on code generation)
    task_8 = TaskNode(
        agent=AgentType.UX_MUSE,
        kind=TaskKind.UX_COPY_AND_MICRODETAILS,
        description="Improve UX copy and microdetails",
        depends_on=[task_3.task_id, task_4.task_id],
        status=Status.PENDING
    )

    # Task 9: Final summary (depends on deployment and UX)
    task_9 = TaskNode(
        agent=AgentType.ORCHESTRATOR,
        kind=TaskKind.FINAL_SUMMARY,
        description="Generate final project summary",
        depends_on=[task_7.task_id, task_8.task_id],
        status=Status.PENDING
    )

    return [task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8, task_9]


def get_next_available_task(task_graph: List[TaskNode]) -> TaskNode:
    """
    Find the next task that can be executed.

    A task is available if:
    - Its status is PENDING
    - All tasks it depends on have status SUCCESS

    Args:
        task_graph: List of all tasks

    Returns:
        Next available TaskNode or None if no tasks are available

    Raises:
        StopIteration: If no tasks are available
    """
    # Create a map of task_id -> task for quick lookup
    task_map = {task.task_id: task for task in task_graph}

    for task in task_graph:
        if task.status != Status.PENDING:
            continue

        # Check if all dependencies are completed
        all_deps_complete = True
        for dep_id in task.depends_on:
            dep_task = task_map.get(dep_id)
            if not dep_task or dep_task.status != Status.SUCCESS:
                all_deps_complete = False
                break

        if all_deps_complete:
            return task

    raise StopIteration("No available tasks to execute")
