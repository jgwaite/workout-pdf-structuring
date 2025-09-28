# Repository Guidelines

## Project Structure & Module Organization
- `models/` Pydantic schemas (Program, Workout, schemes). Avoid free‑form `Dict[...]`; prefer typed objects and key–value lists.
- `services/` API wrappers. `openai_service.py` calls Responses API via `responses.parse(..., text_format=Program)` and handles file uploads.
- `prompts/<name>/<version>/` Versioned Markdown prompts (`system.md`, `user.md`). Keep deterministic and schema‑accurate.
- `scripts/` CLI: `cli.py` (Typer app). Legacy shims: `analyze_pdf.py`, `smoke_openai.py` forward to `programgen`.
- `pdf-programs/` Local PDFs (git‑ignored). `structured_outputs/` JSON results.

## Build, Test, and Development Commands
- Install/lint: `pip install -e . ruff` then `uv run python -m ruff check .` (or `python -m ruff check .` inside the venv).
- Smoke test (Structured Outputs): `uv run programgen smoke --model gpt-5`.
- Parse a PDF: `uv run programgen analyze "pdf-programs/Critical Mass Justin Harris.pdf" --timestamp`.
- Options: `--model`, `--prompt`, `--prompt-version`, `--out-dir`, `--out-file`, `--no-print`, `--timestamp`.

## Coding Style & Naming Conventions
- Python 3.13, 4‑space indentation, type hints required.
- Use Pydantic v2 models; discriminated unions by `scheme.type`.
- Structured Outputs friendly: avoid arbitrary maps; prefer typed models or `parameters: List[SchemeParameter]`.
- Filenames: snake_case modules, singular for models (`workout.py`), verbs for scripts.
- Lint with Ruff; keep functions small and focused.

## Testing Guidelines
- Current: smoke tests only (`scripts/smoke_openai.py`).
- If adding tests, use `pytest` under `tests/` with `test_*.py` naming; include minimal fixtures and sample JSON in `structured_outputs/` (git‑tracked samples OK, no secrets).

## Commit & Pull Request Guidelines
- Commits: present‑tense, scope prefix, concise body.
  - Example: `services: switch to responses.parse with text_format=Program`.
- PRs must include: purpose, summary of changes, run commands used (e.g., smoke/analyze), and before/after notes or sample output path.
- Update README/AGENTS.md and prompts when behavior or schema changes.

## Security & Configuration Tips
- Secrets: set `OPENAI_API_KEY` via environment or `.env` (git‑ignored). Never commit keys or PDFs you don’t own.
- Models: default `OPENAI_MODEL` can be `gpt-5` if your account allows.
- When editing schemas, re‑run the smoke test, then the analyzer; Structured Outputs rejects open‑ended maps and inconsistent `required` lists.
