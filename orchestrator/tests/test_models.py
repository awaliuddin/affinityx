"""
Tests for shared data models.
Validates that all models can be constructed and serialized correctly.
"""
import pytest
from datetime import datetime
from orchestrator.src.models import (
    AgentType,
    Status,
    Severity,
    TaskKind,
    Risk,
    Suggestion,
    ArtifactRef,
    AgentRequest,
    AgentResponse,
    TaskNode,
    DeploymentInfo,
    ProjectState,
    CreateProjectRequest,
    CreateProjectResponse,
    ArchitectResult,
    APIContract,
    DataModel,
    DataModelField,
)


def test_enums():
    """Test that enums are defined correctly"""
    assert AgentType.ARCHITECT == "architect"
    assert Status.PENDING == "pending"
    assert Severity.CRITICAL == "critical"
    assert TaskKind.DEFINE_REQUIREMENTS == "DEFINE_REQUIREMENTS"


def test_risk_model():
    """Test Risk model"""
    risk = Risk(
        severity=Severity.HIGH,
        description="Potential security vulnerability in auth flow"
    )
    assert risk.severity == Severity.HIGH
    assert "security" in risk.description.lower()


def test_artifact_ref():
    """Test ArtifactRef model"""
    artifact = ArtifactRef(
        kind="architecture_spec",
        path="context/artifacts/proj_123_architecture.md",
        summary="Main architecture document"
    )
    assert artifact.kind == "architecture_spec"
    assert artifact.path.endswith(".md")


def test_agent_request():
    """Test AgentRequest model"""
    request = AgentRequest(
        project_id="proj_123",
        task_id="task_456",
        agent=AgentType.ARCHITECT,
        goal="Build a todo list app",
        task_description="Define requirements and architecture",
        constraints={"auth_required": True},
        relevant_context=["User wants simple authentication"],
        payload={"raw_user_idea": "Build a todo list app"}
    )
    assert request.agent == AgentType.ARCHITECT
    assert request.constraints["auth_required"] is True


def test_agent_response():
    """Test AgentResponse model"""
    response = AgentResponse(
        project_id="proj_123",
        task_id="task_456",
        agent=AgentType.ARCHITECT,
        status=Status.SUCCESS,
        artifacts=[
            ArtifactRef(
                kind="architecture_spec",
                path="context/artifacts/proj_123_architecture.md"
            )
        ],
        result={"requirements_count": 5},
        next_suggestions=[
            Suggestion(
                title="Implement backend",
                description="Start with FastAPI backend implementation"
            )
        ],
        risks=[
            Risk(severity=Severity.LOW, description="Consider rate limiting")
        ],
        logs="Architecture spec created successfully"
    )
    assert response.status == Status.SUCCESS
    assert len(response.artifacts) == 1
    assert len(response.next_suggestions) == 1


def test_task_node():
    """Test TaskNode model"""
    task = TaskNode(
        agent=AgentType.ARCHITECT,
        kind=TaskKind.DEFINE_REQUIREMENTS,
        description="Define requirements from user idea",
        depends_on=[],
        status=Status.PENDING
    )
    assert task.agent == AgentType.ARCHITECT
    assert task.status == Status.PENDING
    assert len(task.task_id) > 0  # UUID generated
    assert isinstance(task.created_at, datetime)


def test_project_state_with_full_phase1_graph():
    """Test ProjectState with a complete Phase 1 task graph"""

    # Create tasks in dependency order
    task_1 = TaskNode(
        agent=AgentType.ARCHITECT,
        kind=TaskKind.DEFINE_REQUIREMENTS,
        description="Define requirements from user idea",
        depends_on=[],
        status=Status.PENDING
    )

    task_2 = TaskNode(
        agent=AgentType.ARCHITECT,
        kind=TaskKind.ARCHITECTURE_AND_STACK,
        description="Design architecture and select stack",
        depends_on=[task_1.task_id],
        status=Status.PENDING
    )

    task_3 = TaskNode(
        agent=AgentType.IMPLEMENTER,
        kind=TaskKind.GENERATE_BACKEND_CODE,
        description="Generate backend code",
        depends_on=[task_2.task_id],
        status=Status.PENDING
    )

    task_4 = TaskNode(
        agent=AgentType.IMPLEMENTER,
        kind=TaskKind.GENERATE_FRONTEND_CODE,
        description="Generate frontend code",
        depends_on=[task_2.task_id],
        status=Status.PENDING
    )

    task_5 = TaskNode(
        agent=AgentType.IMPLEMENTER,
        kind=TaskKind.INTEGRATE_AUTH_AND_PERSISTENCE,
        description="Integrate auth and persistence",
        depends_on=[task_2.task_id],
        status=Status.PENDING
    )

    task_6 = TaskNode(
        agent=AgentType.REVIEWER,
        kind=TaskKind.REVIEW_CRITICAL_PATH,
        description="Review critical path code",
        depends_on=[task_3.task_id, task_4.task_id, task_5.task_id],
        status=Status.PENDING
    )

    task_7 = TaskNode(
        agent=AgentType.OPS,
        kind=TaskKind.DEPLOY_APP,
        description="Deploy app to dev environment",
        depends_on=[task_6.task_id],
        status=Status.PENDING
    )

    task_8 = TaskNode(
        agent=AgentType.UX_MUSE,
        kind=TaskKind.UX_COPY_AND_MICRODETAILS,
        description="Improve UX copy and microdetails",
        depends_on=[task_3.task_id, task_4.task_id],
        status=Status.PENDING
    )

    task_9 = TaskNode(
        agent=AgentType.ORCHESTRATOR,
        kind=TaskKind.FINAL_SUMMARY,
        description="Generate final summary",
        depends_on=[task_7.task_id, task_8.task_id],
        status=Status.PENDING
    )

    # Create project state
    project = ProjectState(
        user_id="user_123",
        goal="Build a todo list app with user authentication",
        constraints={"auth_required": True, "preferred_stack": "react"},
        task_graph=[task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8, task_9],
        deployment_info=DeploymentInfo()
    )

    # Validate
    assert len(project.task_graph) == 9
    assert project.task_graph[0].kind == TaskKind.DEFINE_REQUIREMENTS
    assert project.task_graph[-1].kind == TaskKind.FINAL_SUMMARY
    assert all(task.status == Status.PENDING for task in project.task_graph)

    # Validate dependencies
    assert len(project.task_graph[0].depends_on) == 0  # First task has no deps
    assert len(project.task_graph[5].depends_on) == 3  # Review depends on 3 code gen tasks
    assert len(project.task_graph[8].depends_on) == 2  # Final summary depends on deploy + UX

    print(f"✓ Created valid ProjectState with {len(project.task_graph)} tasks")
    return project


def test_create_project_request():
    """Test CreateProjectRequest model"""
    request = CreateProjectRequest(
        user_id="user_123",
        goal="Build a simple todo list app",
        constraints={
            "auth_required": True,
            "preferred_stack": "react"
        }
    )
    assert request.user_id == "user_123"
    assert request.constraints["auth_required"] is True


def test_architect_result():
    """Test ArchitectResult model"""
    result = ArchitectResult(
        functional_requirements=[
            "Users can create todo items",
            "Users can mark items as complete",
            "Users can delete items"
        ],
        non_functional_requirements=[
            "System should respond within 200ms",
            "All data must be encrypted at rest"
        ],
        system_overview="A simple todo list application with user authentication",
        api_contracts=[
            APIContract(
                method="POST",
                path="/api/todos",
                summary="Create a new todo item",
                request_schema={"title": "string", "description": "string"},
                response_schema={"id": "string", "title": "string", "completed": "boolean"}
            )
        ],
        data_model=[
            DataModel(
                table="todos",
                description="Todo items",
                fields=[
                    DataModelField(name="id", type="uuid", nullable=False),
                    DataModelField(name="title", type="string", nullable=False),
                    DataModelField(name="completed", type="boolean", nullable=False)
                ]
            )
        ],
        acceptance_criteria=[
            "User can successfully create and view todos",
            "User authentication works correctly"
        ]
    )
    assert len(result.functional_requirements) == 3
    assert len(result.api_contracts) == 1
    assert result.api_contracts[0].method == "POST"


def test_model_serialization():
    """Test that models can be serialized to/from JSON"""
    project = test_project_state_with_full_phase1_graph()

    # Serialize to dict
    project_dict = project.model_dump()
    assert project_dict["user_id"] == "user_123"
    assert len(project_dict["task_graph"]) == 9

    # Deserialize from dict
    project_restored = ProjectState(**project_dict)
    assert project_restored.user_id == project.user_id
    assert len(project_restored.task_graph) == len(project.task_graph)

    print("✓ Models serialize/deserialize correctly")


if __name__ == "__main__":
    # Run some basic tests
    test_project_state_with_full_phase1_graph()
    test_model_serialization()
    print("\n✅ All model tests passed!")
