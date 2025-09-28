# Contributing

Thanks for your interest in improving this project! This repo is a small, public portfolio project focused on extracting structured workout programs from PDFs using OpenAI Structured Outputs.

## Getting Started
- Clone and create a local env (uv handles it):
  - `cp .env.example .env` and set `OPENAI_API_KEY` (no secrets in commits).
  - `uv run programgen --help` to verify the CLI entry works.
- Optional: run a smoke check (requires an API key):
  - `uv run programgen smoke --model gpt-5`

## Development
- Code style: Python 3.13, type hints, Pydantic v2.
- Linting: `uv run python -m ruff check .`
- CLI commands:
  - Parse: `uv run programgen analyze "pdf-programs/<file>.pdf" --timestamp`
- Prompts live under `prompts/<name>/<version>/{system.md,user.md}`.

## Commit & PR Guidelines
- Commit messages: present tense, scope prefix, concise body.
  - Example: `cli: add Typer entry and shims`
- PRs: include purpose, a brief change summary, and any commands you ran (smoke/analyze).
- No secrets or proprietary PDFs in PRs — use public or dummy files.

## License & IP
- This project uses the Business Source License 1.1 (BSL). See `LICENSE`.
- By contributing, you agree that your contributions are licensed under the repository’s license.

## Questions
Open an issue with a short description. Suggestions for model schema, prompts, or CLI UX are welcome.

