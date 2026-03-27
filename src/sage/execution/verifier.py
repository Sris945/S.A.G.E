"""
SAGE Verification Engine
------------------------
Runs the verification command from a TaskNode after CoderAgent writes a file.
Feeds real stdout/stderr back into the retry loop.

Verification commands come from the planner's `verification` field, e.g.:
  "python -c 'import app'"
  "pytest tests/test_app.py -q"
  "python app.py --help"

Multiple checks: join with `` && `` (space-ampersand-space); each fragment runs
sequentially with ``shell=False`` (no real shell — we split and run in-process).

Workspace: if ``<cwd>/src`` exists, ``PYTHONPATH`` is prefixed with that path so
``import app`` works for ``src/app.py`` layouts (matches Claude-style greenfield).

Safety: ``check_run_command_policy`` (same rules as ``run_command``). Never shell=True.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from sage.execution.exceptions import SafetyViolation
from sage.execution.tool_policy import check_run_command_policy, parse_command_argv

MAX_VERIFY_TIME = 30  # seconds

_CHAIN_SEP = " && "


class VerificationError(Exception):
    pass


def _verification_environ(cwd: Path) -> dict[str, str]:
    """Prefix PYTHONPATH with ./src when present so pytest/imports resolve."""
    env = os.environ.copy()
    src = cwd / "src"
    if src.is_dir():
        extra = str(src.resolve())
        prev = env.get("PYTHONPATH", "").strip()
        if prev:
            env["PYTHONPATH"] = f"{extra}{os.pathsep}{prev}"
        else:
            env["PYTHONPATH"] = extra
    return env


class VerificationEngine:
    def run(self, command: str, cwd: str | None = None) -> dict:
        """
        Run a verification command (or chained commands separated by `` && ``).

        Returns:
          {
            "passed": bool,
            "stdout": str,
            "stderr": str,
            "returncode": int,
            "command": str,
          }
        """
        if not command or not command.strip():
            return {"passed": True, "stdout": "", "stderr": "", "returncode": 0, "command": command}

        root = Path(cwd or Path.cwd()).resolve()
        chunks = [c.strip() for c in command.split(_CHAIN_SEP) if c.strip()]
        if len(chunks) == 1:
            return self._run_one(chunks[0], root)

        out_stdout: list[str] = []
        out_stderr: list[str] = []
        last_rc = 0
        for i, chunk in enumerate(chunks):
            result = self._run_one(chunk, root)
            out_stdout.append(result.get("stdout") or "")
            out_stderr.append(result.get("stderr") or "")
            last_rc = int(result.get("returncode", -1))
            if not result["passed"]:
                print(f"[Verify] ✗ chain step {i + 1}/{len(chunks)} failed (rc={last_rc})")
                return {
                    "passed": False,
                    "stdout": "\n".join(out_stdout),
                    "stderr": "\n".join(out_stderr),
                    "returncode": last_rc,
                    "command": command,
                }
        print(f"[Verify] ✓ passed ({len(chunks)} chained checks, rc={last_rc})")
        return {
            "passed": True,
            "stdout": "\n".join(out_stdout),
            "stderr": "\n".join(out_stderr),
            "returncode": last_rc,
            "command": command,
        }

    def _run_one(self, command: str, cwd: Path) -> dict:
        try:
            check_run_command_policy(command)
        except SafetyViolation as e:
            raise VerificationError(str(e)) from e

        print(f"[Verify] Running: {command}")

        env = _verification_environ(cwd)
        try:
            result = subprocess.run(
                parse_command_argv(command),
                timeout=MAX_VERIFY_TIME,
                capture_output=True,
                text=True,
                shell=False,
                cwd=str(cwd),
                env=env,
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "stdout": "",
                "stderr": f"Verification timed out after {MAX_VERIFY_TIME}s",
                "returncode": -1,
                "command": command,
            }
        except FileNotFoundError as e:
            return {
                "passed": False,
                "stdout": "",
                "stderr": f"Command not found: {e}",
                "returncode": -1,
                "command": command,
            }

        passed = result.returncode == 0
        if passed:
            print(f"[Verify] ✓ passed (rc={result.returncode})")
        else:
            print(f"[Verify] ✗ failed (rc={result.returncode})")
            if result.stderr:
                print(f"[Verify] stderr: {result.stderr[:300]}")

        return {
            "passed": passed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": command,
        }
