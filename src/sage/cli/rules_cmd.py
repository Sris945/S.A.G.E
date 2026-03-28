"""``sage rules`` — inspect merged USER_RULES and run heuristics (spec §18)."""

from __future__ import annotations

import os
from argparse import Namespace
from pathlib import Path
from typing import Any

from sage.cli.exit_codes import EX_USAGE


def cmd_rules(args: Namespace) -> None:
    from sage.prompt_engine.rules_manager import (
        discover_rule_paths,
        load_rule_layers,
        merge_rules_markdown,
        validate_rule_layers,
    )

    base = Path(args.path or ".").resolve()
    if args.repo:
        base = Path(args.repo).expanduser().resolve()
    os.chdir(base)
    os.environ["SAGE_WORKSPACE_ROOT"] = str(base)

    agent = (args.agent or "coder").strip().lower()

    if args.rules_command == "add":
        use_global = bool(getattr(args, "global_rules", False))
        target = (Path.home() / ".sage" / "rules.md") if use_global else (base / ".sage" / "rules.md")
        bits = getattr(args, "rule_text", None) or []
        line = " ".join(str(x) for x in bits).strip()
        if not line:
            print("[SAGE rules] add: empty text.")
            raise SystemExit(EX_USAGE)
        target.parent.mkdir(parents=True, exist_ok=True)
        prefix = "\n" if target.exists() and target.stat().st_size > 0 else ""
        try:
            with open(target, "a", encoding="utf-8") as f:
                f.write(prefix + line + "\n")
        except OSError as e:
            print(f"[SAGE rules] add: could not write {target}: {e}")
            raise SystemExit(EX_USAGE)
        print(f"[SAGE rules] Appended to {target.resolve()}")
        return

    if args.rules_command == "validate":
        layers = load_rule_layers(agent_role=agent, base_dir=base)
        warnings = validate_rule_layers(layers)
        if not warnings:
            print("[SAGE rules] validate: no heuristic issues detected.")
            return
        print("[SAGE rules] validate: warnings (review recommended):")
        for w in warnings:
            print(f"  - {w}")
        if getattr(args, "strict", False):
            raise SystemExit(EX_USAGE)
        return

    # default: show
    paths = discover_rule_paths(agent_role=agent, base_dir=base)
    if args.layers:
        print(f"[SAGE rules] agent_role={agent}  base_dir={base}")
        if not paths:
            print("  (no rule files found)")
            return
        for label, p in paths:
            print(f"  - {label}: {p}")
        print()
    merged = merge_rules_markdown(load_rule_layers(agent_role=agent, base_dir=base))
    if not merged:
        print("[SAGE rules] (empty — no rule files matched)")
        return
    print(merged)


def register_rules_parser(sub: Any) -> None:
    rules_p = sub.add_parser(
        "rules",
        help="Show merged USER_RULES or validate rule files (spec §18)",
    )
    rules_sub = rules_p.add_subparsers(dest="rules_command", required=False)
    add = rules_sub.add_parser(
        "add",
        help="Append a rule line to .sage/rules.md (or ~/.sage/rules.md with --global)",
    )
    add.add_argument(
        "rule_text",
        nargs="+",
        help="Rule sentence(s) to append",
    )
    add.add_argument(
        "--global",
        dest="global_rules",
        action="store_true",
        help="Append to ~/.sage/rules.md instead of project .sage/rules.md",
    )
    val = rules_sub.add_parser(
        "validate",
        help="Heuristic check for unsafe or contradictory rule phrases",
    )
    val.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any warning",
    )
    rules_p.add_argument(
        "--agent",
        default="coder",
        help="Agent role for .sage/rules.{agent}.md (default: coder)",
    )
    rules_p.add_argument(
        "--path",
        default=".",
        help="Project root for resolving .sage/ (default: cwd)",
    )
    rules_p.add_argument(
        "--repo",
        default="",
        help="Same as sage run --repo: chdir before resolving rules",
    )
    rules_p.add_argument(
        "--layers",
        action="store_true",
        help="List contributing file paths before merged markdown",
    )
