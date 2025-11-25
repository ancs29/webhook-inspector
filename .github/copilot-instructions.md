<!-- Copilot instructions for the `webhook-inspector` repo -->

# Quick orientation

- Repo name: `webhook-inspector` — currently a minimal Python project.
- Primary file: `main.py` (present, currently empty). Edit this file for main app logic unless adding a clear multi-file structure.
- Git ignores: see `.gitignore` (virtualenv `venv/`, `__pycache__/`, `.vscode/`, macOS artifacts). Keep these conventions.

# What an AI coding agent should know and do first

1. Treat this as a small Python project. If a feature requires dependencies, add a `requirements.txt` at repo root and document how to run in `README.md`.
2. Use a virtualenv called `venv/` (this is already in `.gitignore`). Typical local workflow:

   - create: `python3 -m venv venv`
   - activate (zsh): `source venv/bin/activate`
   - install: `pip install -r requirements.txt`
   - run: `python main.py`

3. If you add a new tool (formatters, linters, test runner), add its config files and list it in `requirements.txt` and update `README.md` with the exact commands above.

# Coding conventions and repository-specific patterns

- Keep the project single-module until there's a clear need to split: prefer enhancing `main.py` for prototypes/features.
- Respect `.gitignore` when creating new environments, caches, or editor metadata.
- Tests (if added) should live under `tests/` and use `pytest`. Add `pytest` to `requirements.txt` when introducing tests.

# Common edits an agent will perform and how to do them

- Adding dependencies: create or update `requirements.txt`. Do not modify system/global packages.
- Adding a CLI: prefer `argparse` in `main.py` for minimal footprint (no new frameworks unless required).
- Adding an HTTP endpoint: prefer lightweight frameworks (Flask) and only add when justified — include `requirements.txt` and a short run example in `README.md`.

# Commit / PR guidance for the agent

- Keep commits focused and small. Each change that adds a dependency must include a README short note explaining how to run locally.
- PR description should include: what changed, how to run, and a minimal verification checklist (e.g., "run `python main.py` and observe X").

# What not to assume

- The repo currently has no CI, tests, or package metadata. Do not add heavy infra (CI) without user approval.
- No target Python minor version is specified; aim for broad compatibility (Python 3.8+), and document any stricter requirement in `README.md`.

# If you need more context

- Ask the repo owner whether to scaffold a full package layout (src/, setup, CI) or keep things single-file.
- Ask which Python versions to support and whether to use tools like `black`/`isort`/`pytest` before adding them.

---
If any section is unclear or you'd like the agent to follow stricter rules (formatting, testing, CI), tell me and I will update this file.
