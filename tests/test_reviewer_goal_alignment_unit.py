"""Goal-alignment gate: reviewer rejects wrong stack before LLM review."""

import os
import tempfile
import unittest

from sage.agents.reviewer import (
    ReviewerAgent,
    _goal_alignment_issues,
    _reviewer_skip_llm_log_line,
    _static_checks,
)


class TestReviewerGoalAlignment(unittest.TestCase):
    def test_requirements_txt_two_lines_not_flagged_short(self):
        issues = _static_checks(
            "requirements.txt",
            "fastapi>=0.100\nuvicorn[standard]>=0.30\n",
        )
        self.assertFalse(any("short" in i.lower() for i in issues))

    def test_pytest_files_not_flagged_short_two_lines(self):
        issues = _static_checks(
            "tests/test_app.py",
            "def test_x():\n    assert 1\n",
        )
        self.assertFalse(any("short" in i.lower() for i in issues))

    def test_goal_alignment_skips_test_modules(self):
        issues = _goal_alignment_issues(
            "FastAPI app with /health",
            "tests/test_app.py",
            "def test_health():\n    pass\n",
        )
        self.assertEqual(issues, [])

    def test_skip_llm_for_tests_path(self):
        self.assertIn("pytest", _reviewer_skip_llm_log_line("tests/test_app.py").lower())

    def test_helper_detects_missing_fastapi(self):
        issues = _goal_alignment_issues(
            "Implement FastAPI with GET /health in src/app.py",
            "src/app.py",
            "def main():\n  print('hi')\n",
        )
        self.assertTrue(any("fastapi" in i.lower() for i in issues))

    def test_reviewer_fails_before_llm_when_stack_wrong(self):
        fd, path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("def main():\n    return 0\n\nmain()\n")

            out = ReviewerAgent().run(
                file=path,
                task={"id": "t1", "description": "FastAPI app with /health endpoint"},
                memory={},
                insight_sink=None,
            )
            self.assertFalse(out.passed)
            self.assertTrue(out.issues)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
