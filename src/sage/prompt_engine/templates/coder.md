# Coder Instructions

TASK: {task_description}
PROJECT CONTEXT: {project_memory_summary}

RULES:

- **operation** must be exactly ONE of: create, edit, delete, run_command
- **file**: relative path (e.g. `src/app.py`, `requirements.txt`)
- **patch**: **complete file body** for create/edit, or argv-safe command for run_command
- **reason**: one sentence
- **epistemic_flags**: `["INFERRED"]` when guessing; else `[]`
- **Implement exactly what the TASK states** — framework, filenames, routes, and deps. If the TASK says FastAPI + `/health`, deliver that — not a CLI “Hello World”.
- **`requirements.txt`**: pin packages the TASK names (e.g. `fastapi`, `uvicorn[standard]`). One package per line with a compatible version spec when possible.
- **JSON only** for your reply: the `patch` string must be valid JSON — use `\n` for newlines, escape quotes as `\"`, or parsing fails and the run loops.

EXAMPLE (raw JSON only — your patch must be the full file):

{"file":"src/app.py","operation":"create","patch":"from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/health\")\ndef health():\n    return {\"status\": \"ok\"}\n","reason":"FastAPI /health per task","epistemic_flags":[]}

NOW OUTPUT THE JSON FOR THE TASK ABOVE:
