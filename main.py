"""Console entry that delegates to the Typer CLI.

Run via:
  uv run programgen ...
"""

from __future__ import annotations

from scripts.cli import app as _app


def main() -> None:
    _app()


if __name__ == "__main__":
    main()
