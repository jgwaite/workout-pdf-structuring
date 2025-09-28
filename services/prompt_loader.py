from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional


@dataclass
class PromptParts:
    system: str
    user: str


def _read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # Normalize newlines
    return text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"


class _Default(dict):
    def __missing__(self, key):  # type: ignore[override]
        # Return empty string for missing variables instead of raising KeyError.
        return ""


def render(text: str, variables: Optional[Mapping[str, object]] = None) -> str:
    """Very small, safe templating: `str.format_map` with empty defaults.

    - Use `{var}` in prompt files for optional substitutions.
    - Unknown variables render as empty, so prompts are resilient.
    - To write a literal `{` or `}`, double it: `{{` or `}}`.
    """
    if not variables:
        return text
    return text.format_map(_Default(**variables))


def load_prompt(
    *,
    prompts_dir: Path | str,
    name: str,
    version: str,
    variables: Optional[Mapping[str, object]] = None,
) -> PromptParts:
    """Load `system.md` and `user.md` from `<prompts_dir>/<name>/<version>/`.

    Example layout:
        prompts/
          workout_parser/
            v1/
              system.md
              user.md
    """
    root = Path(prompts_dir)
    base = root / name / version
    system_path = base / "system.md"
    user_path = base / "user.md"

    if not system_path.exists() or not user_path.exists():
        missing = [p.name for p in (system_path, user_path) if not p.exists()]
        raise FileNotFoundError(
            f"Missing prompt file(s) in {base}: {', '.join(missing)}"
        )

    system = render(_read_text(system_path), variables)
    user = render(_read_text(user_path), variables)
    return PromptParts(system=system, user=user)

