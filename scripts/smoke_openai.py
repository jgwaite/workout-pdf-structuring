#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from scripts.cli import _smoke_ping, _smoke_upload


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test OpenAI connectivity (shim → Typer)")
    parser.add_argument("--model", type=str, default=None, help="Model override")
    parser.add_argument("--pdf", type=Path, default=None, help="Optional PDF to upload")
    args = parser.parse_args()

    ping = _smoke_ping(args.model)
    print(f"Responses.parse OK: message={ping.message}, model={ping.model or 'n/a'}")

    if args.pdf:
        file_id = _smoke_upload(args.pdf)
        print(f"Files.create OK: file_id={file_id}")


if __name__ == "__main__":
    main()
