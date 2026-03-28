"""
Human checkpoint registry (spec §20).

Maps checkpoint ids to when they run and adds deny-list checks for
pre-destructive approval (checkpoint 4).
"""

from __future__ import annotations

from enum import IntEnum
from pathlib import Path
from typing import Any, Literal

Mode = Literal["research", "auto", "silent"]


class CheckpointId(IntEnum):
    POST_SCAN = 1
    POST_PLAN = 2
    POST_PLAN_WITH_FAILURES = 3
    PRE_DESTRUCTIVE = 4
    INSIGHT_ESCALATION = 5


_SENSITIVE_SEGMENTS = (
    "/.ssh/",
    "/.aws/",
    ".env",
    "id_rsa",
    "credentials.json",
    "secrets.",
    "kubeconfig",
    ".pem",
    "pipeline.yaml",  # CI/CD definition — confirm edits in research mode
)


def _norm_rel(path: str) -> str:
    return str(path).replace("\\", "/").strip()


def is_denylisted_path(file_path: str) -> bool:
    """Paths that always require explicit human approval before apply in research mode."""
    p = _norm_rel(file_path).lower()
    if not p or p.startswith(".."):
        return True
    for seg in _SENSITIVE_SEGMENTS:
        if seg.lower() in p:
            return True
    return False


def should_run_checkpoint(
    checkpoint_id: CheckpointId,
    *,
    mode: str,
    state: dict[str, Any],
) -> bool:
    """
    Whether a checkpoint should run for this mode.

    Auto/silent skip interactive gates; research runs the full matrix subject
    to workflow wiring.
    """
    m = (mode or "research").strip().lower()
    if m in ("auto", "silent"):
        return checkpoint_id in (
            CheckpointId.POST_PLAN_WITH_FAILURES,
            CheckpointId.INSIGHT_ESCALATION,
        )
    return True


def should_checkpoint_pre_apply(
    *,
    file_path: str,
    operation: str,
) -> bool:
    """
    True when research-mode tool apply needs checkpoint 4 (pre-destructive).

    Covers delete/run_command and edits/creates touching deny-listed paths.
    """
    op = (operation or "").strip().lower()
    if op in ("delete", "run_command"):
        return True
    if op in ("edit", "create"):
        return is_denylisted_path(file_path)
    return False


def artifact_root_for_workspace(repo_path: str) -> Path:
    return Path(repo_path or ".").resolve()
