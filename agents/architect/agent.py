"""
Architect Agent - Translates user ideas into concrete architecture specs.
"""
import os
from orchestrator.src.models import (
    AgentRequest,
    AgentResponse,
    ArtifactRef,
    ArchitectResult,
    APIContract,
    DataModel,
    DataModelField,
    Status,
    Risk,
    Severity,
    Suggestion,
)
from tools.repo import file_ops


class ArchitectAgent:
    """
    Architect Agent translates raw user ideas into concrete architecture specs.

    Responsibilities:
    - Extract functional and non-functional requirements
    - Design API contracts
    - Define data models
    - Create system overview
    - Generate acceptance criteria
    """

    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute architecture design task.

        Args:
            request: AgentRequest with raw_user_idea in payload

        Returns:
            AgentResponse with ArchitectResult
        """
        raw_idea = request.payload.get("raw_user_idea", request.goal)

        # Analyze the user idea
        analysis = self._analyze_idea(raw_idea, request.constraints)

        # Generate architecture spec
        architect_result = self._generate_architecture(analysis)

        # Write architecture spec to file
        spec_content = self._format_architecture_spec(architect_result, raw_idea)
        artifacts_dir = f"generated/artifacts"
        file_ops.create_directory(artifacts_dir)
        spec_path = f"{artifacts_dir}/{request.project_id}_architecture.md"
        file_ops.write(spec_path, spec_content)

        # Build response
        return AgentResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            agent=request.agent,
            status=Status.SUCCESS,
            artifacts=[
                ArtifactRef(
                    kind="architecture_spec",
                    path=spec_path,
                    summary=architect_result.system_overview,
                )
            ],
            result=architect_result.model_dump(),
            next_suggestions=[
                Suggestion(
                    title="Implement Backend",
                    description="Start implementing FastAPI backend based on API contracts",
                ),
                Suggestion(
                    title="Implement Frontend",
                    description="Create React frontend for the main user flows",
                ),
            ],
            risks=[
                Risk(
                    severity=Severity.LOW,
                    description="Basic architecture - may need refinement for scale",
                )
            ],
            logs=f"Architecture spec created at {spec_path}. "
            f"Defined {len(architect_result.functional_requirements)} functional requirements, "
            f"{len(architect_result.api_contracts)} API endpoints, "
            f"and {len(architect_result.data_model)} data models.",
        )

    def _analyze_idea(self, idea: str, constraints: dict) -> dict:
        """Analyze user idea to extract key concepts"""
        idea_lower = idea.lower()

        # Detect app type
        app_type = "generic"
        if "todo" in idea_lower or "task" in idea_lower:
            app_type = "todo_list"
        elif "blog" in idea_lower:
            app_type = "blog"
        elif "shop" in idea_lower or "store" in idea_lower:
            app_type = "e_commerce"
        elif "chat" in idea_lower:
            app_type = "chat"
        elif "dashboard" in idea_lower or "analytics" in idea_lower:
            app_type = "dashboard"

        # Detect features
        needs_auth = (
            constraints.get("auth_required", False)
            or "auth" in idea_lower
            or "login" in idea_lower
            or "user" in idea_lower
        )

        needs_realtime = "realtime" in idea_lower or "live" in idea_lower or "chat" in idea_lower

        return {
            "app_type": app_type,
            "needs_auth": needs_auth,
            "needs_realtime": needs_realtime,
            "raw_idea": idea,
            "constraints": constraints,
        }

    def _generate_architecture(self, analysis: dict) -> ArchitectResult:
        """Generate complete architecture based on analysis"""
        app_type = analysis["app_type"]

        # Templates for different app types
        if app_type == "todo_list":
            return self._generate_todo_architecture(analysis)
        elif app_type == "blog":
            return self._generate_blog_architecture(analysis)
        elif app_type == "e_commerce":
            return self._generate_ecommerce_architecture(analysis)
        else:
            return self._generate_generic_architecture(analysis)

    def _generate_todo_architecture(self, analysis: dict) -> ArchitectResult:
        """Generate architecture for a todo list app"""
        return ArchitectResult(
            functional_requirements=[
                "Users can create, read, update, and delete todo items",
                "Users can mark todo items as complete or incomplete",
                "Users can filter todos by status (all, active, completed)",
                "Users can authenticate with email and password",
                "Each user sees only their own todos",
            ],
            non_functional_requirements=[
                "API responses should be under 200ms for 95th percentile",
                "All user data must be encrypted at rest",
                "The application must support at least 100 concurrent users",
            ],
            system_overview="A simple yet powerful todo list application where users can create and manage their tasks. Built with FastAPI backend and React frontend, with PostgreSQL for data persistence.",
            api_contracts=[
                APIContract(
                    method="POST",
                    path="/api/auth/register",
                    summary="Register a new user",
                    request_schema={"email": "string", "password": "string"},
                    response_schema={"user_id": "string", "email": "string", "token": "string"},
                ),
                APIContract(
                    method="POST",
                    path="/api/auth/login",
                    summary="Login user",
                    request_schema={"email": "string", "password": "string"},
                    response_schema={"user_id": "string", "token": "string"},
                ),
                APIContract(
                    method="GET",
                    path="/api/todos",
                    summary="Get all todos for current user",
                    request_schema={},
                    response_schema={"todos": "array"},
                ),
                APIContract(
                    method="POST",
                    path="/api/todos",
                    summary="Create a new todo",
                    request_schema={"title": "string", "description": "string"},
                    response_schema={
                        "id": "string",
                        "title": "string",
                        "description": "string",
                        "completed": "boolean",
                    },
                ),
                APIContract(
                    method="PATCH",
                    path="/api/todos/{id}",
                    summary="Update a todo",
                    request_schema={"title": "string", "description": "string", "completed": "boolean"},
                    response_schema={"id": "string", "title": "string", "completed": "boolean"},
                ),
                APIContract(
                    method="DELETE",
                    path="/api/todos/{id}",
                    summary="Delete a todo",
                    request_schema={},
                    response_schema={"success": "boolean"},
                ),
            ],
            data_model=[
                DataModel(
                    table="users",
                    description="User accounts",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="email", type="string", nullable=False),
                        DataModelField(name="password_hash", type="string", nullable=False),
                        DataModelField(name="created_at", type="timestamp", nullable=False),
                    ],
                ),
                DataModel(
                    table="todos",
                    description="Todo items",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="user_id", type="uuid", nullable=False),
                        DataModelField(name="title", type="string", nullable=False),
                        DataModelField(name="description", type="text", nullable=True),
                        DataModelField(name="completed", type="boolean", nullable=False),
                        DataModelField(name="created_at", type="timestamp", nullable=False),
                        DataModelField(name="updated_at", type="timestamp", nullable=False),
                    ],
                ),
            ],
            acceptance_criteria=[
                "User can successfully register and login",
                "User can create a new todo and see it in the list",
                "User can mark a todo as complete",
                "User can delete a todo",
                "User can only see their own todos",
            ],
        )

    def _generate_blog_architecture(self, analysis: dict) -> ArchitectResult:
        """Generate architecture for a blog app"""
        return ArchitectResult(
            functional_requirements=[
                "Users can create, edit, and delete blog posts",
                "Users can view all published posts",
                "Users can view individual post details",
                "Posts support markdown formatting",
                "Users can authenticate to manage their posts",
            ],
            non_functional_requirements=[
                "Page load time should be under 1 second",
                "Support rich text editing with markdown",
            ],
            system_overview="A modern blogging platform where users can write and publish articles. Features markdown support and clean reading experience.",
            api_contracts=[
                APIContract(
                    method="POST",
                    path="/api/auth/register",
                    summary="Register new user",
                    request_schema={"email": "string", "password": "string", "name": "string"},
                    response_schema={"user_id": "string", "token": "string"},
                ),
                APIContract(
                    method="GET",
                    path="/api/posts",
                    summary="Get all posts",
                    request_schema={},
                    response_schema={"posts": "array"},
                ),
                APIContract(
                    method="POST",
                    path="/api/posts",
                    summary="Create new post",
                    request_schema={"title": "string", "content": "string", "published": "boolean"},
                    response_schema={"id": "string", "title": "string", "slug": "string"},
                ),
                APIContract(
                    method="PUT",
                    path="/api/posts/{id}",
                    summary="Update post",
                    request_schema={"title": "string", "content": "string", "published": "boolean"},
                    response_schema={"id": "string", "updated_at": "timestamp"},
                ),
            ],
            data_model=[
                DataModel(
                    table="users",
                    description="User accounts",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="email", type="string", nullable=False),
                        DataModelField(name="password_hash", type="string", nullable=False),
                        DataModelField(name="name", type="string", nullable=False),
                    ],
                ),
                DataModel(
                    table="posts",
                    description="Blog posts",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="user_id", type="uuid", nullable=False),
                        DataModelField(name="title", type="string", nullable=False),
                        DataModelField(name="slug", type="string", nullable=False),
                        DataModelField(name="content", type="text", nullable=False),
                        DataModelField(name="published", type="boolean", nullable=False),
                        DataModelField(name="created_at", type="timestamp", nullable=False),
                        DataModelField(name="updated_at", type="timestamp", nullable=False),
                    ],
                ),
            ],
            acceptance_criteria=[
                "User can create and publish blog posts",
                "Posts render markdown correctly",
                "Users can edit their own posts",
            ],
        )

    def _generate_generic_architecture(self, analysis: dict) -> ArchitectResult:
        """Generate generic architecture for unknown app types"""
        needs_auth = analysis["needs_auth"]

        api_contracts = [
            APIContract(
                method="GET",
                path="/api/health",
                summary="Health check endpoint",
                request_schema={},
                response_schema={"status": "string"},
            ),
            APIContract(
                method="GET",
                path="/api/items",
                summary="Get all items",
                request_schema={},
                response_schema={"items": "array"},
            ),
            APIContract(
                method="POST",
                path="/api/items",
                summary="Create new item",
                request_schema={"name": "string", "description": "string"},
                response_schema={"id": "string", "name": "string"},
            ),
        ]

        data_models = [
            DataModel(
                table="items",
                description="Main application items",
                fields=[
                    DataModelField(name="id", type="uuid", nullable=False),
                    DataModelField(name="name", type="string", nullable=False),
                    DataModelField(name="description", type="text", nullable=True),
                    DataModelField(name="created_at", type="timestamp", nullable=False),
                ],
            )
        ]

        if needs_auth:
            api_contracts.insert(
                0,
                APIContract(
                    method="POST",
                    path="/api/auth/register",
                    summary="Register new user",
                    request_schema={"email": "string", "password": "string"},
                    response_schema={"user_id": "string", "token": "string"},
                ),
            )
            data_models.insert(
                0,
                DataModel(
                    table="users",
                    description="User accounts",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="email", type="string", nullable=False),
                        DataModelField(name="password_hash", type="string", nullable=False),
                    ],
                ),
            )

        return ArchitectResult(
            functional_requirements=[
                "Users can create and manage items",
                "Users can view all items",
                "System provides RESTful API",
            ] + (["Users can authenticate"] if needs_auth else []),
            non_functional_requirements=[
                "API responses should be fast and reliable",
                "Data must be persisted securely",
            ],
            system_overview=f"A web application for {analysis['raw_idea']}. Built with FastAPI and React.",
            api_contracts=api_contracts,
            data_model=data_models,
            acceptance_criteria=[
                "Users can perform CRUD operations on items",
                "Application is accessible via web browser",
            ],
        )

    def _generate_ecommerce_architecture(self, analysis: dict) -> ArchitectResult:
        """Generate architecture for e-commerce app"""
        return ArchitectResult(
            functional_requirements=[
                "Users can browse products",
                "Users can add products to cart",
                "Users can checkout and place orders",
                "Admin users can manage products",
                "Users must authenticate to place orders",
            ],
            non_functional_requirements=[
                "Support secure payment processing",
                "Handle concurrent transactions safely",
            ],
            system_overview="An e-commerce platform for selling products online with cart and checkout functionality.",
            api_contracts=[
                APIContract(
                    method="GET",
                    path="/api/products",
                    summary="Get all products",
                    request_schema={},
                    response_schema={"products": "array"},
                ),
                APIContract(
                    method="POST",
                    path="/api/cart/add",
                    summary="Add item to cart",
                    request_schema={"product_id": "string", "quantity": "number"},
                    response_schema={"cart": "object"},
                ),
                APIContract(
                    method="POST",
                    path="/api/orders",
                    summary="Create order",
                    request_schema={"cart_items": "array", "shipping_address": "object"},
                    response_schema={"order_id": "string", "total": "number"},
                ),
            ],
            data_model=[
                DataModel(
                    table="products",
                    description="Product catalog",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="name", type="string", nullable=False),
                        DataModelField(name="price", type="decimal", nullable=False),
                        DataModelField(name="stock", type="integer", nullable=False),
                    ],
                ),
                DataModel(
                    table="orders",
                    description="Customer orders",
                    fields=[
                        DataModelField(name="id", type="uuid", nullable=False),
                        DataModelField(name="user_id", type="uuid", nullable=False),
                        DataModelField(name="total", type="decimal", nullable=False),
                        DataModelField(name="status", type="string", nullable=False),
                    ],
                ),
            ],
            acceptance_criteria=[
                "Users can browse and search products",
                "Users can successfully checkout",
            ],
        )

    def _format_architecture_spec(self, result: ArchitectResult, raw_idea: str) -> str:
        """Format architecture result as markdown document"""
        lines = [
            "# Architecture Specification",
            "",
            "## Original Idea",
            f"{raw_idea}",
            "",
            "## System Overview",
            f"{result.system_overview}",
            "",
            "## Functional Requirements",
            "",
        ]

        for i, req in enumerate(result.functional_requirements, 1):
            lines.append(f"{i}. {req}")

        lines.extend(["", "## Non-Functional Requirements", ""])
        for i, req in enumerate(result.non_functional_requirements, 1):
            lines.append(f"{i}. {req}")

        lines.extend(["", "## API Contracts", ""])
        for contract in result.api_contracts:
            lines.append(f"### {contract.method} {contract.path}")
            lines.append(f"{contract.summary}")
            lines.append("")

        lines.extend(["", "## Data Model", ""])
        for model in result.data_model:
            lines.append(f"### {model.table}")
            lines.append(f"{model.description}")
            lines.append("")
            for field in model.fields:
                nullable_str = "nullable" if field.nullable else "required"
                lines.append(f"- **{field.name}** ({field.type}, {nullable_str})")
            lines.append("")

        lines.extend(["", "## Acceptance Criteria", ""])
        for i, criterion in enumerate(result.acceptance_criteria, 1):
            lines.append(f"{i}. {criterion}")

        return "\n".join(lines)
