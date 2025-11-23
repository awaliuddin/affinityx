"""
Test runner utilities.
"""
import subprocess
from typing import Dict


def run_backend_tests() -> Dict[str, any]:
    """
    Run backend tests using pytest.

    Returns:
        Dictionary with test results
    """
    try:
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )

        passed = result.returncode == 0
        summary = result.stdout if passed else result.stderr

        return {
            "passed": passed,
            "summary": summary[:500],  # Truncate for brevity
        }
    except Exception as e:
        return {
            "passed": False,
            "summary": f"Test execution failed: {str(e)}",
        }


def run_frontend_tests() -> Dict[str, any]:
    """
    Run frontend tests using npm test.

    Returns:
        Dictionary with test results
    """
    try:
        result = subprocess.run(
            ["npm", "test", "--", "--run"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="ui"
        )

        passed = result.returncode == 0
        summary = result.stdout if passed else result.stderr

        return {
            "passed": passed,
            "summary": summary[:500],
        }
    except Exception as e:
        return {
            "passed": False,
            "summary": f"Test execution failed: {str(e)}",
        }
