"""
Shared data models for the AI Product Studio.
All agents and services use these strongly-typed models.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


# ==================== ENUMS ====================

class AgentType(str, Enum):
    """Types of agents in the system"""
    ORCHESTRATOR = "orchestrator"
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    REVIEWER = "reviewer"
    OPS = "ops"
    UX_MUSE = "ux_muse"


class Status(str, Enum):
    """Task and response status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class Severity(str, Enum):
    """Risk and issue severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskKind(str, Enum):
    """Types of tasks in the orchestration pipeline"""
    DEFINE_REQUIREMENTS = "DEFINE_REQUIREMENTS"
    ARCHITECTURE_AND_STACK = "ARCHITECTURE_AND_STACK"
    GENERATE_BACKEND_CODE = "GENERATE_BACKEND_CODE"
    GENERATE_FRONTEND_CODE = "GENERATE_FRONTEND_CODE"
    INTEGRATE_AUTH_AND_PERSISTENCE = "INTEGRATE_AUTH_AND_PERSISTENCE"
    REVIEW_CRITICAL_PATH = "REVIEW_CRITICAL_PATH"
    DEPLOY_APP = "DEPLOY_APP"
    UX_COPY_AND_MICRODETAILS = "UX_COPY_AND_MICRODETAILS"
    FINAL_SUMMARY = "FINAL_SUMMARY"


# ==================== PRIMITIVE IDS ====================

ProjectId = str
TaskId = str


# ==================== CORE STRUCTS ====================

class Risk(BaseModel):
    """Represents a risk identified by an agent"""
    severity: Severity
    description: str


class Suggestion(BaseModel):
    """Represents a suggestion for next steps"""
    title: str
    description: str


class ArtifactRef(BaseModel):
    """Reference to an artifact created by an agent"""
    kind: str = Field(..., description="Type of artifact (e.g., 'architecture_spec', 'code_file')")
    path: str = Field(..., description="File path or logical key")
    summary: Optional[str] = None


# ==================== AGENT COMMUNICATION ====================

class AgentRequest(BaseModel):
    """Outer envelope for calling any agent"""
    project_id: ProjectId
    task_id: TaskId
    agent: AgentType
    goal: str = Field(..., description="Global project goal")
    task_description: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    relevant_context: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict, description="Agent-specific payload")


class AgentResponse(BaseModel):
    """Outer envelope returned by any agent"""
    project_id: ProjectId
    task_id: TaskId
    agent: AgentType
    status: Status
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict, description="Agent-specific result")
    next_suggestions: list[Suggestion] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    logs: str = ""


# ==================== TASK MANAGEMENT ====================

class TaskNode(BaseModel):
    """Represents a task in the execution graph"""
    task_id: TaskId = Field(default_factory=lambda: str(uuid4()))
    agent: AgentType
    kind: TaskKind
    description: str
    depends_on: list[TaskId] = Field(default_factory=list)
    status: Status = Status.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== DEPLOYMENT INFO ====================

class DeploymentInfo(BaseModel):
    """Information about deployed application"""
    app_url: Optional[str] = None
    deployment_id: Optional[str] = None
    status: Optional[str] = None


# ==================== PROJECT STATE ====================

class ProjectState(BaseModel):
    """Complete state of a project"""
    project_id: ProjectId = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    goal: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    task_graph: list[TaskNode] = Field(default_factory=list)
    history: list[AgentResponse] = Field(default_factory=list)
    deployment_info: DeploymentInfo = Field(default_factory=DeploymentInfo)
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== API MODELS ====================

class CreateProjectRequest(BaseModel):
    """Request to create a new project"""
    user_id: str
    goal: str
    constraints: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "goal": "Build a simple todo list app with user authentication",
                "constraints": {
                    "preferred_stack": "react",
                    "auth_required": True,
                    "target_region": "us-east-1",
                    "budget_tier": "free"
                }
            }
        }


class CreateProjectResponse(BaseModel):
    """Response after creating a project"""
    project_id: ProjectId
    task_graph: list[TaskNode]


class GetProjectStatusResponse(BaseModel):
    """Response with current project status"""
    project: ProjectState


# ==================== AGENT-SPECIFIC PAYLOADS ====================

# Architect Agent
class ArchitectRequestPayload(BaseModel):
    """Payload for Architect agent requests"""
    raw_user_idea: str
    existing_requirements: Optional[str] = None


class APIContract(BaseModel):
    """API endpoint contract"""
    method: str
    path: str
    summary: str
    request_schema: dict[str, Any] = Field(default_factory=dict)
    response_schema: dict[str, Any] = Field(default_factory=dict)


class DataModelField(BaseModel):
    """Field in a data model"""
    name: str
    type: str
    nullable: bool = False


class DataModel(BaseModel):
    """Data model (table) definition"""
    table: str
    description: str
    fields: list[DataModelField]


class ArchitectResult(BaseModel):
    """Result from Architect agent"""
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    system_overview: str
    api_contracts: list[APIContract]
    data_model: list[DataModel]
    acceptance_criteria: list[str]


# Implementer Agent
class ImplementerRequestPayload(BaseModel):
    """Payload for Implementer agent requests"""
    architecture_spec: str
    work_scope: str = Field(..., description="backend | frontend | full_stack | auth_persistence")
    target_paths: list[str] = Field(default_factory=list)


class FileInfo(BaseModel):
    """Information about a file"""
    path: str
    content: str


class TestInfo(BaseModel):
    """Information about tests"""
    added: list[str] = Field(default_factory=list)
    notes: str = ""


class ImplementerResult(BaseModel):
    """Result from Implementer agent"""
    files_created: list[FileInfo] = Field(default_factory=list)
    files_modified: list[FileInfo] = Field(default_factory=list)
    tests: TestInfo = Field(default_factory=TestInfo)


# Reviewer Agent
class ReviewerRequestPayload(BaseModel):
    """Payload for Reviewer agent requests"""
    requirements_summary: str
    files_to_review: list[str]
    run_tests: bool = False


class ReviewIssue(BaseModel):
    """Issue found during review"""
    severity: Severity
    location: str
    description: str
    fix_hint: str


class TestsResult(BaseModel):
    """Result of test execution"""
    executed: bool
    summary: str


class ReviewerResult(BaseModel):
    """Result from Reviewer agent"""
    overall_verdict: str = Field(..., description="pass | fail | pass_with_risks")
    issues: list[ReviewIssue] = Field(default_factory=list)
    tests_result: TestsResult = Field(default_factory=lambda: TestsResult(executed=False, summary=""))


# Ops Agent
class OpsRequestPayload(BaseModel):
    """Payload for Ops agent requests"""
    deployment_target: str = "dev_default"
    env_config: dict[str, Any] = Field(default_factory=dict)
    repo_ref: str = ""


class OpsResult(BaseModel):
    """Result from Ops agent"""
    deployment_status: str = Field(..., description="success | partial | failed")
    deployment_id: Optional[str] = None
    app_url: Optional[str] = None
    logs_excerpt: Optional[str] = None


# UX Muse Agent
class UXMuseRequestPayload(BaseModel):
    """Payload for UX Muse agent requests"""
    user_persona: str
    primary_flow: str
    front_end_paths: list[str]


class Microcopy(BaseModel):
    """UX microcopy suggestions"""
    landing_headline: str
    subheadline: str
    cta_text: str


class UXChange(BaseModel):
    """UX change to a file"""
    path: str
    content: str


class UXMuseResult(BaseModel):
    """Result from UX Muse agent"""
    microcopy: Microcopy
    ui_suggestions: list[str] = Field(default_factory=list)
    changes: list[UXChange] = Field(default_factory=list)
