# Architecture implementation status

This table tracks parity with the architecture specification (see `sage plan/` or project architecture docs). It is the **source of truth** for shipped behavior versus future work.

| Spec area | Feature | Status | Notes |
|-----------|---------|--------|-------|
| §3 Codebase intelligence | Tree-sitter / semantic maps | Partial | `context_builder`, `semantic_reader`; vector index: `codebase/code_index.py`, Qdrant under `.sage/qdrant_code_index/` |
| §3 | Retrieved chunks in prompts | Partial | `ensure_index_for_brief` → `retrieved_code_chunks` in brief; embedded in `CODEBASE CONTEXT` |
| §11 Intel feed | Composite risk + preempt | Implemented | `intelligence_feed.py`, `should_preempt`, coder fallback wiring |
| §11 | Reviewer pre-injection | Implemented | `prefix_builder` + `get_reviewer_coder_high_notes` |
| §11 | Intervention logging | Implemented | `ORCHESTRATOR_INTERVENTION` with `action_taken` where applicable |
| §20 HITL | Checkpoints 1–5 | Partial | `workflow.human_checkpoint*`; registry: `orchestrator/checkpoints.py` |
| §20 | Plan reject / edit | Implemented | Post-plan `a`/`r`/`e` in research mode; `.sage/last_plan.json` + `--resume` |
| §20 | Checkpoint 4 sensitive paths | Implemented | `should_checkpoint_pre_apply`, deny-listed paths |
| §18 Rules | Merge / validate | Implemented | `rules_manager`; `sage rules add` |
| §16 Memory | 3-layer retrieval | Documented | `memory/manager.py` docstring; RAG + patterns in orchestrator |
| §16 | Weekly digest | Implemented | `sage memory digest` → `memory/weekly_digest.md` |
| §8 Epistemic | `[UNVERIFIED]` gate | Partial | Blocks completion in `verification_gate` when tests missing |
| §9 Parallelism | Conflict UX | Partial | `merge_task_updates` panel for file-lock blocks |
| §22 Observability | Run metrics JSON | Implemented | `.sage/last_run_metrics.json` via `run_metrics.py` |
| §23 Benchmarks | Six YAML cases + 8 metrics | Partial | `src/sage/benchmarks/tasks/*.yaml`; `metrics_notes` for stubs |
| Research / RL | Export + BC/CQL | Partial | `sage rl export`, `train_bc`, `train_cql`, `scripts/train_routing_policy.py` |
| Dashboard (§22 future) | Live web UI | Not planned (substitute) | Structured JSON + TTY summary |

**Banner for spec checklists:** If an older checklist in a long-form architecture document disagrees with this file, **trust `ARCHITECTURE_STATUS.md`**.
