"""CLI and legacy script shims for program-generator.

The canonical CLI is implemented in `scripts/cli.py` using Typer.
`scripts/analyze_pdf.py` and `scripts/smoke_openai.py` are kept as thin shims
to ease transition from the old argparse-based flow.
"""

