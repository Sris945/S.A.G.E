"""Planner merges duplicate DAG nodes (same description + deps + agent)."""

from sage.agents.planner import _dedupe_task_nodes
from sage.protocol.schemas import TaskNode


def test_dedupe_drops_parallel_clones():
    nodes = [
        TaskNode(
            id="task_001",
            description="Add requirements.txt",
            dependencies=[],
            assigned_agent="coder",
            verification="true",
        ),
        TaskNode(
            id="task_002",
            description="Implement src/app.py with FastAPI",
            dependencies=["task_001"],
            assigned_agent="coder",
            verification="python -m py_compile src/app.py",
        ),
        TaskNode(
            id="task_003",
            description="Implement src/app.py with FastAPI",
            dependencies=["task_001"],
            assigned_agent="coder",
            verification="python -m py_compile src/app.py",
        ),
        TaskNode(
            id="task_004",
            description="Write tests",
            dependencies=["task_003"],
            assigned_agent="test_engineer",
            verification="pytest -q",
        ),
    ]
    out = _dedupe_task_nodes(nodes)
    assert len(out) == 3
    ids = {n.id for n in out}
    assert "task_003" not in ids
    tests = next(n for n in out if n.id == "task_004")
    assert tests.dependencies == ["task_002"]
