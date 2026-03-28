# Install & bootstrap (Linux / Windows)

## Where to run `startup.sh`

**`startup.sh` / `startup.ps1` live in the SAGE repository root only.** They create a `.venv` **next to the clone** and `pip install -e` the `sage` package.

- **Install / upgrade SAGE:** `cd /path/to/SAGE` (your git clone) → `bash startup.sh` → `source .venv/bin/activate`.
- **Your app or experiment repo:** use `sage init` there; do **not** expect `startup.sh` to exist in that folder unless you copied it yourself.

---

## Quick path (recommended)

From the **SAGE repository root**:

### Linux / macOS

```bash
chmod +x startup.sh
./startup.sh
source .venv/bin/activate
sage doctor
sage
```

Or:

```bash
bash startup.sh && source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
.\startup.ps1
.\.venv\Scripts\Activate.ps1
sage doctor
sage
```

The scripts:

1. Create **`.venv`** next to the repo if missing.
2. **Upgrade pip** and install the package in editable mode with **dev** and **tui** extras: `pip install -e ".[dev,tui]"` (tests/linters + `sage tui`).
3. Print activation hints.

---

## Requirements

- **Python 3.10+** on `PATH` (`python3` on Linux, `python` on Windows).
- Optional: **Ollama** for local models (see `README.md` and `docs/models.md`).

---

## Environment variables (optional)

| Variable | Purpose |
|----------|---------|
| `SAGE_REPO_URL` | Base URL for repo/doc links in the CLI (`sage` shell help footer). |
| `PYTHON` | Linux only: override interpreter for `startup.sh` (default `python3`). |

---

## Manual install (no scripts)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip wheel setuptools
pip install -e ".[dev,tui]"
```

Minimal runtime only (no tests, no Textual TUI): `pip install -e .`

Entry point: `sage` (see `pyproject.toml` `[project.scripts]`).

---

## Optional: venv inside a project folder

`sage doctor` reports **venv: OK** if you are inside an activated virtualenv **or** if `./.venv` exists. To silence the venv warning in a random directory:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e /path/to/SAGE   # editable install of your clone
```

---

## Next steps

- **Overview & project workflow:** `README.md`
- **CLI modes and env:** `docs/CLI.md`
- **Getting started (bench, rl):** `docs/getting_started.md`
- **Models / Ollama:** `docs/models.md`
