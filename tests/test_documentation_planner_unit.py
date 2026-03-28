"""Planner wiring for the documentation agent role."""

from __future__ import annotations

from pathlib import Path

from sage.agents import planner as planner_mod
from sage.protocol.schemas import TaskNode


def test_validate_dag_accepts_documentation_alias() -> None:
    dag = {
        "nodes": [
            {
                "id": "t1",
                "description": "Refresh API overview",
                "dependencies": [],
                "assigned_agent": "docs",
                "verification": "python -c \"from pathlib import Path; assert Path('README.md').is_file()\"",
            }
        ]
    }
    nodes = planner_mod._validate_dag(dag)
    assert len(nodes) == 1
    assert nodes[0].assigned_agent == "documentation"


def test_upgrade_readme_task_to_documentation() -> None:
    dag = {
        "nodes": [
            {
                "id": "t1",
                "description": "Expand README with install instructions",
                "dependencies": [],
                "assigned_agent": "coder",
                "verification": "",
            }
        ]
    }
    nodes = planner_mod._validate_dag(dag)
    assert nodes[0].assigned_agent == "documentation"


def test_postprocess_requirements_generic_without_fastapi_in_user_goal() -> None:
    """Planner hallucination: FastAPI in task text must not force FastAPI requirements verify."""
    nodes = [
        TaskNode(
            id="t1",
            description="Add requirements.txt with dependencies from the GOAL.",
            dependencies=[],
            assigned_agent="coder",
            verification="python -m py_compile src/requirements.txt",
        )
    ]
    out = planner_mod._postprocess_task_nodes(
        nodes, user_goal="Create src/hello.py with greet() returning hello"
    )
    assert "py_compile" not in out[0].verification
    assert "pathlib" in out[0].verification


def test_postprocess_fills_empty_doc_verification() -> None:
    nodes = [
        TaskNode(
            id="t1",
            description="Add CONTRIBUTING guide",
            dependencies=[],
            assigned_agent="documentation",
            verification="",
        )
    ]
    out = planner_mod._postprocess_task_nodes(nodes, user_goal="docs")
    assert "CONTRIBUTING.md" in out[0].verification
    assert "assert" in out[0].verification


def test_planner_template_rejects_health_only_copy_paste_example() -> None:
    """Regression: embedded /health JSON caused models to ignore real user goals."""
    text = Path(planner_mod.TEMPLATE_PATH).read_text(encoding="utf-8")
    assert "GET /health returning" not in text
    assert "Never" in text and "Hello World" in text
    assert "{task_description}" in text
