"""
End-of-run metrics bundle (spec §22) — written to ``.sage/last_run_metrics.json``.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_METRICS_VERSION = "1.0"


def _session_log_path() -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return Path("memory") / "sessions" / f"{today}.log"


def _parse_log_for_session(session_id: str) -> dict[str, Any]:
    """Aggregate events from today's journal for this ``session_id``."""
    out: dict[str, Any] = {
        "prompt_quality_deltas": [],
        "human_checkpoints_reached": 0,
        "orchestrator_interventions": 0,
        "agent_insights_emitted": 0,
        "fix_pattern_events": 0,
        "models_from_events": [],
    }
    log_path = _session_log_path()
    if not log_path.exists():
        return out
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("session_id") != session_id:
            continue
        et = ev.get("type") or ""
        if et == "PROMPT_QUALITY_DELTA":
            qd = ev.get("quality_delta")
            if qd is None and "payload" in ev:
                qd = (ev.get("payload") or {}).get("quality_delta")
            if qd is not None:
                try:
                    out["prompt_quality_deltas"].append(float(qd))
                except (TypeError, ValueError):
                    pass
        elif et == "HUMAN_CHECKPOINT_REACHED":
            out["human_checkpoints_reached"] = int(out.get("human_checkpoints_reached") or 0) + 1
        elif et == "ORCHESTRATOR_INTERVENTION":
            out["orchestrator_interventions"] += 1
        elif et == "AGENT_INSIGHT_EMITTED":
            out["agent_insights_emitted"] += 1
        elif et in ("FIX_PATTERN_APPLIED", "FIX_PATTERN_HIT"):
            out["fix_pattern_events"] += 1
        elif et == "MODEL_ROUTING_DECISION":
            sel = ev.get("selected_model") or (ev.get("payload") or {}).get("selected_model")
            if sel:
                out["models_from_events"].append(str(sel))
    return out


def _local_vs_cloud_ratio(models_used: dict[str, int]) -> float | None:
    """
    Fraction of invocations assumed local (Ollama-style tags) vs cloud (anthropic, openai, bedrock, claude in name).
    """
    if not models_used:
        return None
    local = 0
    cloud = 0
    cloud_pat = re.compile(
        r"anthropic|claude|openai|gpt-|bedrock|azure|vertex|gemini",
        re.I,
    )
    for name, n in models_used.items():
        n = int(n)
        if cloud_pat.search(name):
            cloud += n
        else:
            local += n
    tot = local + cloud
    if tot == 0:
        return None
    return local / tot


def _histogram_from_task_dag(state: dict[str, Any]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for n in (state.get("task_dag") or {}).get("nodes") or []:
        if not isinstance(n, dict):
            continue
        m = (n.get("model_used") or "").strip()
        if m:
            hist[m] = hist.get(m, 0) + 1
    return hist


def build_run_metrics(state: dict[str, Any]) -> dict[str, Any]:
    """Build the spec §22 metrics object (JSON-serializable)."""
    session_id = (os.environ.get("SAGE_SESSION_ID") or "").strip()
    log_agg = _parse_log_for_session(session_id) if session_id else {}

    nodes = (state.get("task_dag") or {}).get("nodes") or []
    total = len(nodes)
    completed = sum(1 for n in nodes if isinstance(n, dict) and n.get("status") == "completed")
    failed = sum(1 for n in nodes if isinstance(n, dict) and n.get("status") == "failed")
    blocked = sum(1 for n in nodes if isinstance(n, dict) and n.get("status") == "blocked")

    deltas = log_agg.get("prompt_quality_deltas") or []
    if deltas:
        prompt_quality_delta = sum(deltas) / len(deltas)
    else:
        prompt_quality_delta = None

    models_hist = _histogram_from_task_dag(state)
    for m in log_agg.get("models_from_events") or []:
        models_hist[m] = models_hist.get(m, 0) + 1

    started = (state.get("session_memory") or {}).get("run_started_at_utc")
    ended = datetime.now(timezone.utc).isoformat()

    return {
        "metrics_version": _METRICS_VERSION,
        "run_id": session_id or None,
        "trace_id": (os.environ.get("SAGE_TRACE_ID") or "").strip() or None,
        "repo_mode": state.get("repo_mode") or "greenfield",
        "ended_at_utc": ended,
        "tasks_total": total,
        "tasks_completed": completed,
        "tasks_failed": failed,
        "tasks_blocked": blocked,
        "debug_loop_iterations": int(state.get("debug_attempts") or 0),
        "fix_pattern_hits": int(log_agg.get("fix_pattern_events") or 0),
        "fix_pattern_applied_flag": bool(state.get("fix_pattern_applied")),
        "agent_insights_emitted": int(log_agg.get("agent_insights_emitted") or 0),
        "orchestrator_interventions": int(log_agg.get("orchestrator_interventions") or 0),
        "human_checkpoints_reached": int(log_agg.get("human_checkpoints_reached") or 0),
        "models_used": models_hist,
        "prompt_quality_delta": prompt_quality_delta,
        "local_vs_cloud_ratio": _local_vs_cloud_ratio(models_hist),
        "plan_only": bool(state.get("plan_only")),
        "dry_run": bool(state.get("dry_run")),
        "last_error_preview": (state.get("last_error") or "")[:2000] or None,
        "started_at_utc": started,
    }


def write_run_metrics_json(state: dict[str, Any], *, base_dir: Path | None = None) -> Path | None:
    """Write ``.sage/last_run_metrics.json`` under cwd or ``base_dir``."""
    root = Path(base_dir or Path.cwd()).resolve()
    sage = root / ".sage"
    try:
        sage.mkdir(parents=True, exist_ok=True)
        path = sage / "last_run_metrics.json"
        payload = build_run_metrics(state)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
    except OSError:
        return None


def stamp_run_start_utc(state: dict[str, Any]) -> dict[str, Any]:
    """Merge into session_memory for duration metrics (optional)."""
    sm = dict(state.get("session_memory") or {})
    if "run_started_at_utc" not in sm:
        sm["run_started_at_utc"] = datetime.now(timezone.utc).isoformat()
    return {**state, "session_memory": sm}
