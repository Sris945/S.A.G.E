# Planner Instructions

TASK: {task_description}
PROJECT CONTEXT: {project_memory_summary}

RULES (product-grade / “IDE assistant” bar):

- Break work into **small, concrete** tasks. Prefer **4–7 goal-aligned tasks** when the goal needs UI + API + tests + docs; **3 tasks minimum** only if the goal is truly tiny.
- **One task per distinct unit of work** — do **not** emit multiple parallel nodes with the **same** `description` and `dependencies` (e.g. three identical “Implement `src/app.py`…” tasks). Merge into a single node.
- **Mirror the user’s literal goal.** If they name **FastAPI**, **Flask**, **Django**, **Click**, **Typer**, etc., the plan must implement **that** stack — not a generic stub.
- **Never** ship a plan that only implements **`/health`**, **`Hello World`**, or a bare JSON `{"message":"..."}` **unless the user explicitly asked for exactly that.** If the GOAL mentions a **calculator**, **HTML page**, **POST /api/...**, **evaluate**, **form**, **dashboard**, etc., every implementation task must name those **routes, files, and behaviors** in its `description`.
- When the user asks for a **web UI + backend** (single page, calculator, form, SPA shell):
  - Include **one coder task** for **`requirements.txt`** (deps the stack needs: `fastapi`, `uvicorn[standard]`, etc.).
  - Include **one coder task** for **`src/app.py`** (or the path they asked for) with:
    - `FastAPI()` instance named **`app`** (importable as `from app import app` when `PYTHONPATH=src`).
    - **`GET /`** (or `/index.html`) serving **HTML** for the UI when the user asked for a page.
    - **`POST` (or `GET`) endpoints** the user named for evaluation / API — **not** only `/health`.
  - Include **test_engineer** tasks whose assertions **import strings or routes from the GOAL** (e.g. test `POST /api/eval` returns JSON, test `GET /` contains `calculator` or the widget they asked for) — **not** only `GET /health` unless health was requested.
  - Include a **documentation** task for **`README.md`** with the **exact** run command, e.g. `PYTHONPATH=src uvicorn app:app --reload` (or `uvicorn app:app --app-dir src` depending on layout) — so the user is not told `uvicorn main:app` when the module is `src/app.py`.
- When the user asks for an **HTTP API** without a special UI, still plan **dependency manifest → implementation → tests**; tests must assert **the routes and behaviors in the GOAL**, not a generic health probe unless they asked for health checks.
- **verification**: one shell-safe command per task. Chain with **` && `** when needed. Use only `python`, `python -m`, `pytest`, etc. — no pipes, `sudo`, or downloads.
- **assigned_agent** must be exactly ONE of: coder, architect, reviewer, test_engineer, documentation
- For **documentation** work: use **documentation** agent; verification must assert the file exists and has substance.
- **dependencies**: list of task IDs that must complete first (`[]` if none)
- **brainstorm_questions**: 0–4 short questions **only** if the goal is genuinely ambiguous. If you can plan confidently, use `[]` and set **confirmed** `true`.
- **confirmed**: boolean — `true` if the goal is clear enough to build a DAG without user input

## Output format

Emit **one** JSON object (no markdown fences, no commentary). Shape:

```json
{"brainstorm_questions":[],"confirmed":true,"dag":{"nodes":[ ... ]}}
```

Each node: `id`, `description`, `dependencies`, `assigned_agent`, `verification`.

## Critical

The **example below is structural only**. Your `description` and `verification` fields must **track the TASK and GOAL above** — **do not** copy example routes if the user asked for something different (e.g. do not default to `/health` for a calculator app).

**Illustrative nodes** (replace descriptions with the real GOAL’s features):

- `task_001` — Add `requirements.txt` with dependencies from the GOAL. `assigned_agent`: **coder**.
- `task_002` — Implement `src/app.py`: FastAPI `app`, routes and behavior **as specified in the GOAL** (HTML shell, POST handler, safe eval, etc.). `assigned_agent`: **coder**. `dependencies`: `["task_001"]`. Verification must use **`python -m py_compile …`** (not bare `py_compile`) and import-check `app`.
- `task_003` — `tests/test_app.py`: **TestClient** (or equivalent) assertions that **fail** if the GOAL’s main behavior is missing (not only a health string). `assigned_agent`: **test_engineer**. `dependencies`: `["task_002"]`. `verification`: `pytest tests/test_app.py -q`
- `task_004` — `README.md`: how to install and run (correct `uvicorn` / `PYTHONPATH`). `assigned_agent`: **documentation**. `dependencies`: `["task_002"]`.

If the GOAL is smaller, merge steps — but **do not** omit the user’s requested surfaces (pages, APIs, files).

NOW OUTPUT THE JSON FOR THE TASK ABOVE (raw JSON only, single object):
