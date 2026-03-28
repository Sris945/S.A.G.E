#!/usr/bin/env python3
"""
Train routing policy from exported JSONL (BC then CQL-style bandit).

Calls ``sage.rl.train_bc`` and ``sage.rl.train_cql`` in-process so CI and local
dev share one entrypoint (spec research track / benchmark gate).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="Train SAGE routing policy from routing JSONL")
    p.add_argument("--data", required=True, help="routing_v1.jsonl from `sage rl export`")
    p.add_argument("--out-bc", default="memory/rl/policy_bc.joblib", help="BC checkpoint path")
    p.add_argument("--out-cql", default="memory/rl/policy_cql.joblib", help="CQL checkpoint path")
    p.add_argument("--skip-cql", action="store_true", help="Run BC only")
    args = p.parse_args()

    data = Path(args.data)
    if not data.is_file():
        print(f"[train_routing_policy] missing dataset: {data}", file=sys.stderr)
        raise SystemExit(2)

    from sage.rl.train_bc import train_bc_joblib
    from sage.rl.train_cql import train_cql_stub

    train_bc_joblib(data, Path(args.out_bc))
    print(f"[train_routing_policy] BC checkpoint: {Path(args.out_bc).resolve()}")
    if args.skip_cql:
        return
    train_cql_stub(data, Path(args.out_cql))
    print(f"[train_routing_policy] CQL checkpoint: {Path(args.out_cql).resolve()}")


if __name__ == "__main__":
    main()
