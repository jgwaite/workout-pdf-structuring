# Workout PDF Parser
Turn high‑quality workout PDFs into clean, typed JSON using OpenAI Structured Outputs and Pydantic. Ships a small Typer CLI and versioned prompts — great for analysis, customization, or feeding other tools.

Why?
Most programs in the wild are rigid. Extracting rich structure (e.g., blocks, tempos, RIR) enables smarter, more personal programming and analysis.

**What’s included**
- Responses API integration with structured output (Pydantic models)
- Versioned, file‑based prompts
- Typer CLI (`programgen`) to parse a PDF and write JSON to `structured_outputs/`

## Quick Start
- Copy the example env and set your key:
  - `cp .env.example .env` then put your `OPENAI_API_KEY`.
  - Defaults: `OPENAI_MODEL` (repo defaults to `gpt-4o-mini` if unset), `PROMPTS_DIR=prompts`, `PROMPT_NAME=workout_parser`, `PROMPT_VERSION=v1`.
- Run with `uv` (no global installs needed):
  - Smoke test: `uv run programgen smoke --model gpt-5`
  - Parse a PDF: `uv run programgen analyze "pdf-programs/Critical Mass Justin Harris.pdf" --timestamp`
  - Options: `--model`, `--prompt`, `--prompt-version`, `--no-print`, `--out-dir`, `--out-file`, `--timestamp`

## Responses API + Pydantic
We call the OpenAI Responses API and ask it to return a structure that validates as `models.Program` (Pydantic). The service handles:
- Uploading the PDF via the Files API
- Sending versioned prompts (`system.md` + `user.md`)
- Parsing directly into the `Program` model

Key files
- Service: `services/openai_service.py`
- Models: `models/workout.py` (`Program`, `Workout`, `Exercise`, `SetPrescription`, etc.)
- CLI: console entry `programgen` → `scripts/cli.py` (via `main.py`)
- Legacy shims: `scripts/analyze_pdf.py`, `scripts/smoke_openai.py` (forward to `programgen`)
- Prompts: `prompts/workout_parser/v1/{system.md,user.md}`

Minimal code usage
```py
from services import OpenAIService

svc = OpenAIService()
program = svc.parse_program_from_pdf(
    "pdf-programs/my-program.pdf",
    prompt_name="workout_parser",
    prompt_version="v1",
)
print(program.model_dump_json(indent=2))
```

## Smoke Test
Verify connectivity and optionally the Files API:

- Ping test (structured outputs): `uv run programgen smoke --model gpt-5`
  - Prints: `Responses.parse OK: message=pong, model=...`
- Files API upload: `uv run programgen smoke --pdf "pdf-programs/Critical Mass Justin Harris.pdf"`
  - Prints the created `file_id`.

## Prompt Versioning
Prompts are plain Markdown files on disk, so you can iterate, diff, and review them like code.

Layout
```
prompts/
  <name>/
    <version>/
      system.md
      user.md
```

Configure defaults in `.env` and override per‑run with CLI flags:
- Env: `PROMPTS_DIR`, `PROMPT_NAME`, `PROMPT_VERSION`
- CLI: `--prompt <name>`, `--prompt-version <version>`

Best practices (simple, not overbuilt)
- Use two files per prompt: put strict rules/schema in `system.md`, task + small realistic example in `user.md`.
- Keep examples accurate to the schema (keys/shape must match `Program`). One good example beats many toy ones.
- Make instructions deterministic: “Return only the JSON object that matches the schema.” Specify how to handle unknowns.
- Version by folder (`v1`, `v2`, …). Don’t edit old versions; make a new one and change the default.
- Use tiny templating only when needed: `{model}` etc. Unknown vars render empty; escape braces with `{{` `}}`.
- Add a short change note at the top of `system.md` when you cut a new version.

<!-- PDF→image utilities removed from this repo to keep the scope tight. -->

## Linting
- Run Ruff from the venv: `uv run python -m ruff check .`

## License
Business Source License 1.1 (BSL, source‑available). See `LICENSE` for terms.
- Additional Use Grant: non‑production and internal evaluation; limited production use up to 5 seats.
- Change Date: 2029‑01‑01 → automatically re‑licenses this version as Apache 2.0 on/after that date.

## Troubleshooting
- “No module named pip”: bootstrap with `python -m ensurepip --upgrade`.
- “ruff: command not found”: use `python -m ruff check .` from the venv.
- API auth errors: ensure `OPENAI_API_KEY` is set in `.env` or environment.
- File not found for prompts: check `prompts/<name>/<version>/{system.md,user.md}` paths and set `PROMPT_NAME`/`PROMPT_VERSION` accordingly.
