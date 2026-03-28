# Documentation

The **authoritative overview** for contributors and users is the repository **[`README.md`](../README.md)** at the repo root (install, features, architecture summary, and the full doc map).

This page is a **compact index** of files in `docs/`:

| File | Topic |
|------|--------|
| [INSTALL.md](INSTALL.md) | Clone, `startup.sh` / `startup.ps1`, venv |
| [CLI.md](CLI.md) | `sage run`, shell, rules, memory, env vars |
| [getting_started.md](getting_started.md) | Init + run flow; `bench`, `rl`, `sim` |
| [ARCHITECTURE_STATUS.md](ARCHITECTURE_STATUS.md) | Spec vs shipped features |
| [architecture.md](architecture.md) | Design entrypoints |
| [architecture_diagram.md](architecture_diagram.md) | Diagrams |
| [models.md](models.md) | Ollama, `models.yaml`, VRAM |
| [event_bus.md](event_bus.md) | Event bus semantics |
| [TRUST_AND_SCALE.md](TRUST_AND_SCALE.md) | Policy and scale |
| [LIVE_TESTING.md](LIVE_TESTING.md) | Live Ollama verification |

**Tip:** Set `SAGE_REPO_URL` so the `sage` shell’s `/commands` footer links to your GitHub fork.
