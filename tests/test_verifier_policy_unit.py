"""Verification commands use the same policy as tool execution."""

import sys

import pytest

from sage.execution.verifier import (
    VerificationEngine,
    VerificationError,
    normalize_verification_command_line,
)


def test_verifier_blocks_denied_substring():
    with pytest.raises(VerificationError, match="Blocked"):
        VerificationEngine().run("sudo apt update")


def test_verifier_runs_safe_command(tmp_path):
    r = VerificationEngine().run("echo ok", cwd=str(tmp_path))
    assert r["passed"] is True
    assert "ok" in (r.get("stdout") or "")


def test_verifier_chained_commands(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 42\n", encoding="utf-8")
    cmd = (
        "python -m py_compile src/app.py && python -c "
        "\"import sys; sys.path.insert(0, 'src'); import app; assert app.x == 42\""
    )
    r = VerificationEngine().run(cmd, cwd=str(tmp_path))
    assert r["passed"] is True


def test_verifier_normalizes_bare_py_compile(tmp_path):
    """LLMs sometimes emit ``py_compile`` as argv0; we map to ``python -m py_compile``."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    r = VerificationEngine().run("py_compile src/app.py", cwd=str(tmp_path))
    assert r["passed"] is True


def test_normalize_rewrites_py_compile_on_requirements_txt():
    """py_compile on requirements.txt parses pins as Python source; rewrite to pathlib check."""
    bad = "python -m py_compile src/requirements.txt"
    fixed = normalize_verification_command_line(bad)
    assert "py_compile" not in fixed
    assert "requirements.txt" in fixed
    assert "pathlib" in fixed


def test_verifier_requirements_txt_rewrite_passes(tmp_path):
    (tmp_path / "requirements.txt").write_text("pytest>=7\n", encoding="utf-8")
    r = VerificationEngine().run("python -m py_compile requirements.txt", cwd=str(tmp_path))
    assert r["passed"] is True


def test_verifier_pytest_gets_src_on_path(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(
        "import sys\nsys.path.insert(0, 'src')\nimport app\n\ndef test_f():\n    assert app.f() == 1\n",
        encoding="utf-8",
    )
    r = VerificationEngine().run(
        f"{sys.executable} -m pytest tests/test_x.py -q", cwd=str(tmp_path)
    )
    assert r["passed"] is True
