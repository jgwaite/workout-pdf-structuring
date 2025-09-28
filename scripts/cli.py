from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
import re

import typer
from pydantic import BaseModel

from services import OpenAIService


app = typer.Typer(add_completion=False, no_args_is_help=True, help="Program generator CLI (PDF → structured Program)")


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def _analyze_impl(
    pdf: Path,
    *,
    model: Optional[str],
    prompt: Optional[str],
    prompt_version: Optional[str],
    out_dir: Path,
    out_file: Optional[Path],
    timestamp: bool,
    print_json: bool,
) -> Path:
    service = OpenAIService()
    program = service.parse_program_from_pdf(
        pdf,
        model=model,
        prompt_name=prompt,
        prompt_version=prompt_version,
    )

    ts = datetime.now().strftime("%Y%m%d-%H%M%S") if timestamp else None

    if out_file:
        out_path = out_file
        if timestamp:
            stem, suffix = out_path.stem, (out_path.suffix or ".json")
            out_path = out_path.with_name(f"{stem}-{ts}{suffix}")
        if out_path.suffix.lower() != ".json":
            out_path = out_path.with_suffix(".json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = _slugify(pdf.stem) if pdf.stem else "program"
        filename = f"{stem}.json" if not ts else f"{stem}-{ts}.json"
        out_path = out_dir / filename

    out_path.write_text(program.model_dump_json(indent=2), encoding="utf-8")
    if print_json:
        typer.echo(program.model_dump_json(indent=2))

    return out_path


@app.command("analyze")
def analyze(
    pdf: Path = typer.Argument(..., help="Path to a local PDF file"),
    model: Optional[str] = typer.Option(None, help="Override model (defaults from env, e.g. gpt-4o-mini or gpt-5)"),
    prompt: Optional[str] = typer.Option(None, help="Prompt name (defaults to PROMPT_NAME)"),
    prompt_version: Optional[str] = typer.Option(None, help="Prompt version (defaults to PROMPT_VERSION)"),
    out_dir: Path = typer.Option(Path("structured_outputs"), help="Directory to write JSON (default: structured_outputs)"),
    out_file: Optional[Path] = typer.Option(None, help="Explicit JSON output path (overrides --out-dir)"),
    timestamp: bool = typer.Option(False, help="Append timestamp to output filename"),
    print_json: bool = typer.Option(True, "--print/--no-print", help="Print JSON to stdout as well"),
) -> None:
    """Analyze a PDF and extract a structured Program JSON."""
    try:
        out_path = _analyze_impl(
            pdf,
            model=model,
            prompt=prompt,
            prompt_version=prompt_version,
            out_dir=out_dir,
            out_file=out_file,
            timestamp=timestamp,
            print_json=print_json,
        )
    except Exception as exc:  # keep the CLI noisy
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(f"Wrote structured output to: {out_path}", fg=typer.colors.GREEN)


class _Ping(BaseModel):
    message: str
    model: Optional[str] = None


def _smoke_ping(model: Optional[str]) -> _Ping:
    svc = OpenAIService()
    chosen = model or svc.config.model
    resp = svc.client.responses.parse(
        model=chosen,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Return a JSON object with message='pong' and the model name.",
                    }
                ],
            }
        ],
        text_format=_Ping,
    )
    if hasattr(resp, "output_parsed") and resp.output_parsed is not None:
        return resp.output_parsed
    return _Ping.model_validate(resp)


def _smoke_upload(pdf: Optional[Path]) -> Optional[str]:
    if not pdf:
        return None
    svc = OpenAIService()
    return svc.upload_file(pdf)


@app.command("smoke")
def smoke(
    model: Optional[str] = typer.Option(None, help="Model to use for the ping (defaults from env)"),
    pdf: Optional[Path] = typer.Option(None, help="Optional PDF to upload to verify Files API"),
) -> None:
    """Connectivity test for Responses.parse and optional Files upload."""
    try:
        ping = _smoke_ping(model)
        typer.echo(f"Responses.parse OK: message={ping.message}, model={ping.model or 'n/a'}")
        file_id = _smoke_upload(pdf)
        if file_id:
            typer.echo(f"Files.create OK: file_id={file_id}")
    except Exception as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def main() -> None:  # console entrypoint
    app()


if __name__ == "__main__":
    main()
