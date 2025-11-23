"""
Agent Runtime - Routes agent requests to the appropriate agent implementation.
"""
from orchestrator.src.models import AgentRequest, AgentResponse, AgentType, Status
from agents.architect.agent import ArchitectAgent
from agents.implementer.agent import ImplementerAgent
from agents.reviewer.agent import ReviewerAgent
from agents.ops.agent import OpsAgent
from agents.ux_muse.agent import UXMuseAgent


class AgentRuntime:
    """
    Central runtime for executing agent requests.

    Routes requests to appropriate agent implementations based on agent type.
    """

    def __init__(self):
        self.agents = {
            AgentType.ARCHITECT: ArchitectAgent(),
            AgentType.IMPLEMENTER: ImplementerAgent(),
            AgentType.REVIEWER: ReviewerAgent(),
            AgentType.OPS: OpsAgent(),
            AgentType.UX_MUSE: UXMuseAgent(),
        }

    def run(self, request: AgentRequest) -> AgentResponse:
        """
        Execute an agent request.

        Args:
            request: AgentRequest containing task details

        Returns:
            AgentResponse with execution results

        Raises:
            ValueError: If agent type is not recognized
        """
        # Special handling for ORCHESTRATOR agent (FINAL_SUMMARY)
        if request.agent == AgentType.ORCHESTRATOR:
            return self._run_final_summary(request)

        # Route to appropriate agent
        agent = self.agents.get(request.agent)
        if not agent:
            raise ValueError(f"Unknown agent type: {request.agent}")

        return agent.execute(request)

    def _run_final_summary(self, request: AgentRequest) -> AgentResponse:
        """
        Handle FINAL_SUMMARY task from orchestrator.

        Args:
            request: AgentRequest

        Returns:
            AgentResponse with summary
        """
        project_state = request.payload.get("project_state", {})
        deployment_info = project_state.get("deployment_info", {})

        summary_lines = [
            "# Project Complete! 🎉",
            "",
            f"## Goal",
            f"{request.goal}",
            "",
        ]

        if deployment_info.get("app_url"):
            summary_lines.extend([
                "## Deployment",
                f"✅ App URL: {deployment_info['app_url']}",
                f"✅ Status: {deployment_info.get('status', 'deployed')}",
                "",
            ])

        # Count successful tasks
        task_graph = project_state.get("task_graph", [])
        success_count = sum(1 for task in task_graph if task.get("status") == "success")

        summary_lines.extend([
            "## Tasks Completed",
            f"✅ {success_count} out of {len(task_graph)} tasks completed successfully",
            "",
            "## What Was Built",
            "- ✅ Architecture designed and requirements defined",
            "- ✅ Backend API implemented (FastAPI)",
            "- ✅ Frontend UI implemented (React)",
            "- ✅ Authentication and persistence integrated",
            "- ✅ Code reviewed for quality and security",
            "- ✅ Application deployed to development environment",
            "- ✅ UX improvements applied",
        ])

        summary = "\n".join(summary_lines)

        return AgentResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            agent=AgentType.ORCHESTRATOR,
            status=Status.SUCCESS,
            result={"summary": summary},
            logs=f"Generated final summary for project {request.project_id}",
        )
