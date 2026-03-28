## Getting started

### 1. Install SAGE (repository clone)

From the **SAGE repo root** (where `startup.sh` lives):

- **Linux/macOS:** `bash startup.sh && source .venv/bin/activate`
- **Windows:** `.\startup.ps1` and activate `.venv`

Details → **[INSTALL.md](INSTALL.md)**.

### 2. Prepare a project directory

```bash
mkdir -p ~/myproject && cd ~/myproject
sage init
```

This creates `.sage/`, `memory/`, starter rules, and pytest hints. **`sage init` does not install the SAGE package** — run `startup.sh` from the clone for that.

### 3. Run

```bash
export SAGE_MODEL_PROFILE=test   # optional — one small model per role (laptop/CI)
sage doctor
sage run "Your goal here" --auto
```

- **`--research`** (default) — interactive plan checkpoints (`a` / `r` / `e`).
- **`--auto`** / **`--silent`** — less interaction; see **[CLI.md](CLI.md)**.

Overview and first-run tips → **[README.md](../README.md)**. CLI reference → **[CLI.md](CLI.md)**. **Spec vs implementation:** **[ARCHITECTURE_STATUS.md](ARCHITECTURE_STATUS.md)**.

---

### Benchmarks & RL (reference)

- `sage bench`
- `sage bench --compare-policy` — static vs learned routing (needs checkpoints)

**Phase 5 — offline RL**

- `sage rl collect-synth --rows 650`
- `sage rl export --output datasets/routing_v1.jsonl`
- `sage rl analyze-rewards --data datasets/routing_v1.jsonl`
- `sage rl train-bc --data datasets/routing_v1.jsonl`
- `sage rl train-cql --data datasets/routing_v1.jsonl`
- `sage rl eval-offline --data datasets/routing_v1.jsonl --checkpoint memory/rl/policy_cql.joblib`
- `scripts/train_routing_policy.py` — BC then CQL in one script (from repo root with venv activated)

**Phase 6 — simulator**

- `sage sim generate --count 1000 --out datasets/sim_tasks.jsonl`
- `sage sim run --tasks datasets/sim_tasks.jsonl --workers 4`
- `docker build -f sim/Dockerfile -t sage-sim:latest .`
- `sage sim run --tasks datasets/sim_tasks.jsonl --workers 4 --docker`
