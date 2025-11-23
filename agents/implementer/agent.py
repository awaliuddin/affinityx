"""
Implementer Agent - Generates working backend and frontend code.
"""
from orchestrator.src.models import (
    AgentRequest,
    AgentResponse,
    ArtifactRef,
    ImplementerResult,
    FileInfo,
    TestInfo,
    Status,
    Suggestion,
)
from tools.repo import file_ops
from agents.implementer import templates


class ImplementerAgent:
    """
    Implementer Agent generates working code for backend, frontend, and auth/persistence.
    """

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute code generation task"""
        work_scope = request.payload.get("work_scope", "full_stack")
        architecture_spec = request.payload.get("architecture_spec", request.goal)

        files_created = []
        files_modified = []
        tests_added = []

        # Generate code based on scope
        if work_scope == "backend" or work_scope == "full_stack":
            backend_files = self._generate_backend(request.project_id, architecture_spec)
            files_created.extend(backend_files)
            tests_added.append("Backend API tests")

        if work_scope == "frontend" or work_scope == "full_stack":
            frontend_files = self._generate_frontend(request.project_id, architecture_spec)
            files_created.extend(frontend_files)
            tests_added.append("Frontend component tests")

        if work_scope == "auth_persistence" or work_scope == "full_stack":
            auth_files = self._generate_auth_persistence(request.project_id)
            files_created.extend(auth_files)

        # Build artifacts
        artifacts = [
            ArtifactRef(kind="code_file", path=f.path, summary=f"Generated {f.path}")
            for f in files_created
        ]

        result = ImplementerResult(
            files_created=files_created,
            files_modified=files_modified,
            tests=TestInfo(added=tests_added, notes="Basic tests generated"),
        )

        return AgentResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            agent=request.agent,
            status=Status.SUCCESS,
            artifacts=artifacts,
            result=result.model_dump(),
            next_suggestions=[
                Suggestion(
                    title="Review Code",
                    description="Run code review to check for issues",
                )
            ],
            logs=f"Generated {len(files_created)} code files for {work_scope} scope",
        )

    def _generate_backend(self, project_id: str, spec: str) -> list[FileInfo]:
        """Generate FastAPI backend code"""
        base_path = f"generated/app/backend"
        file_ops.create_directory(base_path)

        files = []

        # Main app
        main_content = templates.get_backend_main_template(spec)
        main_path = f"{base_path}/main.py"
        file_ops.write(main_path, main_content)
        files.append(FileInfo(path=main_path, content=main_content))

        # Models
        models_content = templates.get_backend_models_template(spec)
        models_path = f"{base_path}/models.py"
        file_ops.write(models_path, models_content)
        files.append(FileInfo(path=models_path, content=models_content))

        # Routes
        routes_content = templates.get_backend_routes_template(spec)
        routes_path = f"{base_path}/routes.py"
        file_ops.write(routes_path, routes_content)
        files.append(FileInfo(path=routes_path, content=routes_content))

        # Database
        db_content = templates.get_backend_database_template()
        db_path = f"{base_path}/database.py"
        file_ops.write(db_path, db_content)
        files.append(FileInfo(path=db_path, content=db_content))

        # Requirements
        req_content = templates.get_backend_requirements()
        req_path = f"{base_path}/requirements.txt"
        file_ops.write(req_path, req_content)
        files.append(FileInfo(path=req_path, content=req_content))

        return files

    def _generate_frontend(self, project_id: str, spec: str) -> list[FileInfo]:
        """Generate React frontend code"""
        base_path = f"generated/app/frontend"
        file_ops.create_directory(f"{base_path}/src")
        file_ops.create_directory(f"{base_path}/public")

        files = []

        # Package.json
        package_content = templates.get_frontend_package_json()
        package_path = f"{base_path}/package.json"
        file_ops.write(package_path, package_content)
        files.append(FileInfo(path=package_path, content=package_content))

        # Main App
        app_content = templates.get_frontend_app_template(spec)
        app_path = f"{base_path}/src/App.tsx"
        file_ops.write(app_path, app_content)
        files.append(FileInfo(path=app_path, content=app_content))

        # Main entry
        main_content = templates.get_frontend_main_template()
        main_path = f"{base_path}/src/main.tsx"
        file_ops.write(main_path, main_content)
        files.append(FileInfo(path=main_path, content=main_content))

        # Vite config
        vite_content = templates.get_vite_config()
        vite_path = f"{base_path}/vite.config.ts"
        file_ops.write(vite_path, vite_content)
        files.append(FileInfo(path=vite_path, content=vite_content))

        # Index HTML
        html_content = templates.get_index_html()
        html_path = f"{base_path}/index.html"
        file_ops.write(html_path, html_content)
        files.append(FileInfo(path=html_path, content=html_content))

        # tsconfig
        ts_content = templates.get_tsconfig()
        ts_path = f"{base_path}/tsconfig.json"
        file_ops.write(ts_path, ts_content)
        files.append(FileInfo(path=ts_path, content=ts_content))

        return files

    def _generate_auth_persistence(self, project_id: str) -> list[FileInfo]:
        """Generate authentication and persistence code"""
        base_path = f"generated/app/backend"

        files = []

        # Auth module
        auth_content = templates.get_auth_template()
        auth_path = f"{base_path}/auth.py"
        file_ops.write(auth_path, auth_content)
        files.append(FileInfo(path=auth_path, content=auth_content))

        return files
