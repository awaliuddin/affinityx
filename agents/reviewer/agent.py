"""
Reviewer Agent - Provides quality and security review.
"""
from orchestrator.src.models import (
    AgentRequest,
    AgentResponse,
    ReviewerResult,
    ReviewIssue,
    TestsResult,
    Status,
    Severity,
    Suggestion,
)
from tools.repo import file_ops
from tools.tests import runner


class ReviewerAgent:
    """
    Reviewer Agent checks code for quality and security issues.
    """

    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute code review task"""
        files_to_review = request.payload.get("files_to_review", [])
        run_tests = request.payload.get("run_tests", False)
        requirements_summary = request.payload.get("requirements_summary", "")

        issues = []
        tests_result = TestsResult(executed=False, summary="Tests not run")

        # Review files for common issues
        for file_path in files_to_review:
            if file_ops.file_exists(file_path):
                content = file_ops.read(file_path)
                file_issues = self._review_file(file_path, content, requirements_summary)
                issues.extend(file_issues)

        # Run tests if requested
        if run_tests:
            backend_result = runner.run_backend_tests()
            tests_result = TestsResult(
                executed=True,
                summary=f"Backend tests: {'PASSED' if backend_result['passed'] else 'FAILED'}. {backend_result['summary'][:200]}"
            )

        # Determine overall verdict
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        high_issues = [i for i in issues if i.severity == Severity.HIGH]

        if critical_issues or (run_tests and not backend_result.get('passed', True)):
            overall_verdict = "fail"
        elif high_issues:
            overall_verdict = "pass_with_risks"
        else:
            overall_verdict = "pass"

        result = ReviewerResult(
            overall_verdict=overall_verdict,
            issues=issues,
            tests_result=tests_result,
        )

        return AgentResponse(
            project_id=request.project_id,
            task_id=request.task_id,
            agent=request.agent,
            status=Status.SUCCESS if overall_verdict != "fail" else Status.PARTIAL,
            result=result.model_dump(),
            next_suggestions=[
                Suggestion(
                    title="Deploy App",
                    description="Code review passed, ready for deployment",
                )
            ] if overall_verdict == "pass" else [],
            logs=f"Reviewed {len(files_to_review)} files. Found {len(issues)} issues. Verdict: {overall_verdict}",
        )

    def _review_file(self, file_path: str, content: str, requirements: str) -> list[ReviewIssue]:
        """Review a single file for issues"""
        issues = []

        # Check for hardcoded secrets
        if "SECRET_KEY = \"your-secret-key" in content or "password123" in content:
            issues.append(
                ReviewIssue(
                    severity=Severity.HIGH,
                    location=file_path,
                    description="Hardcoded secret or default password detected",
                    fix_hint="Use environment variables for secrets",
                )
            )

        # Check for missing error handling
        if ".py" in file_path and "try:" not in content and "async def" in content:
            issues.append(
                ReviewIssue(
                    severity=Severity.MEDIUM,
                    location=file_path,
                    description="Missing error handling in async functions",
                    fix_hint="Add try-except blocks for database operations",
                )
            )

        # Check for SQL injection risks
        if "execute(" in content and "f\"" in content:
            issues.append(
                ReviewIssue(
                    severity=Severity.CRITICAL,
                    location=file_path,
                    description="Potential SQL injection vulnerability",
                    fix_hint="Use parameterized queries instead of string formatting",
                )
            )

        # Check for CORS issues
        if "allow_origins=[\"*\"]" in content:
            issues.append(
                ReviewIssue(
                    severity=Severity.LOW,
                    location=file_path,
                    description="Overly permissive CORS configuration",
                    fix_hint="Restrict CORS to specific origins in production",
                )
            )

        return issues
