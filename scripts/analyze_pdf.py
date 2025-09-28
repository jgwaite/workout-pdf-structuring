#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from scripts.cli import _analyze_impl


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a PDF and extract a structured Program (shim → Typer)"
    )
    parser.add_argument("pdf", type=Path, help="Path to a local PDF file")
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--prompt", type=str, default=None)
    parser.add_argument("--prompt-version", type=str, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("structured_outputs"))
    parser.add_argument("--no-print", action="store_true")
    parser.add_argument("--out-file", type=Path, default=None)
    parser.add_argument("--timestamp", action="store_true")
    args = parser.parse_args()

    out_path = _analyze_impl(
        args.pdf,
        model=args.model,
        prompt=args.prompt,
        prompt_version=args.prompt_version,
        out_dir=args.out_dir,
        out_file=args.out_file,
        timestamp=args.timestamp,
        print_json=(not args.no_print),
    )

    print(f"\nWrote structured output to: {out_path}")


if __name__ == "__main__":
    main()
