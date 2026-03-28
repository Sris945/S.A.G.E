"""Run report builder and humanized verify labels."""

from sage.cli.run_output import (
    RunReport,
    build_run_report,
    humanize_verify_command,
    run_output_level,
)


def test_humanize_verify_command() -> None:
    assert "Compile" in humanize_verify_command("python -m py_compile src/app.py")
    assert humanize_verify_command("pytest tests/ -q") == "Run pytest"
    assert humanize_verify_command("python -m pytest tests/x.py -q") == "Run pytest"


def test_build_run_report_minimal() -> None:
    r = build_run_report(
        {
            "user_prompt": "Build a calculator",
            "task_dag": {
                "nodes": [
                    {
                        "id": "task_001",
                        "status": "completed",
                        "description": "Add deps",
                        "assigned_agent": "coder",
                    }
                ]
            },
            "artifacts_by_task": {"task_001": "requirements.txt"},
            "last_error": "",
        }
    )
    assert isinstance(r, RunReport)
    assert "calculator" in r.goal
    assert r.completed == 1
    assert r.artifacts == [("task_001", "requirements.txt")]


def test_build_run_report_fastapi_hint() -> None:
    r = build_run_report(
        {
            "user_prompt": "x",
            "task_dag": {"nodes": []},
            "artifacts_by_task": {"t": "src/app.py"},
            "last_error": "",
        }
    )
    assert "uvicorn" in r.how_to_run_hint or "PYTHONPATH" in r.how_to_run_hint


def test_run_output_level_default(monkeypatch) -> None:
    monkeypatch.delenv("SAGE_RUN_OUTPUT", raising=False)
    assert run_output_level() == "summary"


def test_run_output_level_debug(monkeypatch) -> None:
    monkeypatch.setenv("SAGE_RUN_OUTPUT", "debug")
    assert run_output_level() == "debug"
