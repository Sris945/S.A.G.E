"""Planner JSON: accept array output; heuristic split on fallback."""

from __future__ import annotations

from sage.agents import planner as planner_mod
from sage.protocol.schemas import TaskNode


def test_extract_json_wraps_top_level_array() -> None:
    raw = (
        '[{"id":"task_001","description":"Do X","dependencies":[],"assigned_agent":"coder",'
        '"verification":""}]'
    )
    d = planner_mod._extract_json(raw)
    assert "dag" in d
    assert len(d["dag"]) == 1


def test_heuristic_split_hello_and_test() -> None:
    prompt = (
        "Create src/hello.py with def greet(): return 'hello' and "
        "tests/test_hello.py with pytest for greet()"
    )
    nodes = planner_mod._heuristic_library_plus_test_tasks(prompt)
    assert nodes is not None
    assert len(nodes) == 2
    assert nodes[0].assigned_agent == "coder"
    assert nodes[1].assigned_agent == "test_engineer"
    assert nodes[1].dependencies == ["task_001"]


def test_heuristic_split_none_without_paths() -> None:
    assert planner_mod._heuristic_library_plus_test_tasks("refactor everything") is None


def test_repair_replaces_fastapi_template_when_goal_names_hello() -> None:
    """Model returns canned FastAPI DAG; user asked for hello.py + test_hello."""
    prompt = (
        "Create src/hello.py with def greet(): return 'hello' and "
        "tests/test_hello.py with pytest for greet()"
    )
    bad = [
        TaskNode(
            id="task_001",
            description="Add requirements.txt with dependencies from the GOAL.",
            dependencies=[],
            assigned_agent="coder",
        ),
        TaskNode(
            id="task_002",
            description="Implement src/app.py: FastAPI app, routes and behavior.",
            dependencies=["task_001"],
            assigned_agent="coder",
        ),
        TaskNode(
            id="task_003",
            description="tests/test_app.py: TestClient assertions",
            dependencies=["task_002"],
            assigned_agent="test_engineer",
        ),
        TaskNode(
            id="task_004",
            description="README.md: uvicorn",
            dependencies=["task_002"],
            assigned_agent="documentation",
        ),
    ]
    fixed = planner_mod._repair_dag_if_goal_mismatch(prompt, bad)
    assert len(fixed) == 2
    assert "hello.py" in fixed[0].description.lower()
    assert fixed[1].assigned_agent == "test_engineer"
