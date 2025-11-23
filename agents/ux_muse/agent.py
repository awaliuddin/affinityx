"""
UX Muse Agent - Improves UX copy and microdetails.
"""
from orchestrator.src.models import (
    AgentRequest,
    AgentResponse,
    UXMuseResult,
    Microcopy,
    UXChange,
    Status,
)
from tools.repo import file_ops


class UXMuseAgent:
    """
    UX Muse Agent improves user experience through better copy and microdetails.
    """

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute UX improvement task"""
        user_persona = request.payload.get("user_persona", "end user")
        primary_flow = request.payload.get("primary_flow", request.goal)
        front_end_paths = request.payload.get("front_end_paths", [])

        # Generate microcopy based on the primary flow
        microcopy = self._generate_microcopy(primary_flow, user_persona)

        # Generate UI suggestions
        ui_suggestions = [
            "Add loading states for async operations",
            "Improve error messages with actionable guidance",
            "Add empty states with friendly illustrations",
            "Improve button labels to be more action-oriented",
            "Add tooltips for complex features",
        ]

        # Apply improvements to frontend files
        changes = []
        for path in front_end_paths:
            if file_ops.file_exists(path) and "App" in path:
                content = file_ops.read(path)
                improved_content = self._improve_frontend_copy(content, microcopy)
                if improved_content != content:
                    file_ops.write(path, improved_content)
                    changes.append(UXChange(path=path, content=improved_content))

        result = UXMuseResult(
            microcopy=microcopy,
            ui_suggestions=ui_suggestions,
            changes=changes,
        )

        return AgentResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            agent=request.agent,
            status=Status.SUCCESS,
            result=result.model_dump(),
            logs=f"Applied UX improvements to {len(changes)} files. Generated microcopy and {len(ui_suggestions)} suggestions.",
        )

    def _generate_microcopy(self, primary_flow: str, persona: str) -> Microcopy:
        """Generate engaging microcopy"""
        flow_lower = primary_flow.lower()

        if "todo" in flow_lower or "task" in flow_lower:
            return Microcopy(
                landing_headline="Get Things Done",
                subheadline="Simple, powerful task management for busy people",
                cta_text="Start Organizing",
            )
        elif "blog" in flow_lower:
            return Microcopy(
                landing_headline="Share Your Story",
                subheadline="Beautiful blogging platform for writers and creators",
                cta_text="Start Writing",
            )
        elif "shop" in flow_lower or "store" in flow_lower:
            return Microcopy(
                landing_headline="Your Store, Online",
                subheadline="Sell anything, anywhere, with ease",
                cta_text="Open Your Store",
            )
        else:
            return Microcopy(
                landing_headline="Transform Your Workflow",
                subheadline="Built for people who value simplicity and power",
                cta_text="Get Started",
            )

    def _improve_frontend_copy(self, content: str, microcopy: Microcopy) -> str:
        """Improve copy in frontend code"""
        # Replace generic headlines
        content = content.replace("<h1>My App</h1>", f"<h1>{microcopy.landing_headline}</h1>")
        content = content.replace("<h1>Welcome</h1>", f"<h1>{microcopy.landing_headline}</h1>")

        # Improve button labels
        content = content.replace("Add Item", "Create New Item")
        content = content.replace(">Login</button>", f">{microcopy.cta_text}</button>")

        # Improve empty states
        content = content.replace(
            "No items yet. Create one above!",
            "No items yet. Start by creating your first one!"
        )

        return content
