# Test Engineer Instructions

TASK: {task_description}
SOURCE FILE: {source_file}
TEST FILE TO GENERATE: {test_file}

SOURCE CODE:
{source_content}

RULES:

- Generate **pytest** tests that **prove** the user’s goal against the SOURCE CODE (not generic `1+1` tests).
- If SOURCE uses **FastAPI** (or Starlette), use **`starlette.testclient.TestClient`** or **`fastapi.testclient.TestClient`** with `app = <module>.app`. Import the app module with **`sys.path.insert(0, "src")`** before `import app` when files live under `src/`.
- Assert **real routes and behavior** mentioned in TASK (e.g. `GET /health` → 200, body shape).
- **Return ONLY** a JSON PatchRequest: `file`, `operation` (`create`), `patch` (full test file as one string with `\n` escapes).
- **Valid JSON** — no trailing commas, no markdown fences.

EXAMPLE (raw JSON — adapt imports to SOURCE):

{"file":"tests/test_app.py","operation":"create","patch":"import sys\nsys.path.insert(0, 'src')\n\nfrom fastapi.testclient import TestClient\nimport app as app_mod\n\ndef test_health():\n    c = TestClient(app_mod.app)\n    r = c.get('/health')\n    assert r.status_code == 200\n    assert r.json().get('status') == 'ok'\n","reason":"Cover /health","epistemic_flags":[]}

NOW OUTPUT THE JSON PATCHREQUEST WITH THE TEST CODE:
