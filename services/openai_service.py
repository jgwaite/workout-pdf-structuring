from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv
from openai import OpenAI

from models.workout import Program
from .prompt_loader import load_prompt


@dataclass
class OpenAIConfig:
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompts_dir: str = os.getenv("PROMPTS_DIR", "prompts")
    prompt_name: str = os.getenv("PROMPT_NAME", "workout_parser")
    prompt_version: str = os.getenv("PROMPT_VERSION", "v1")

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        load_dotenv(override=False)
        return cls(
            api_key=os.getenv("OPENAI_API_KEY") or None,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            prompts_dir=os.getenv("PROMPTS_DIR", "prompts"),
            prompt_name=os.getenv("PROMPT_NAME", "workout_parser"),
            prompt_version=os.getenv("PROMPT_VERSION", "v1"),
        )


class OpenAIService:
    """Thin wrapper around the OpenAI Responses API for PDF → structured data.

    Key features:
    - Upload a PDF file to the Files API
    - Call the Responses API with an `input_file` to analyze the PDF
    - Parse directly into a Pydantic model using structured output
    """

    def __init__(self, config: Optional[OpenAIConfig] = None):
        self.config = config or OpenAIConfig.from_env()
        # The official SDK reads API key from env automatically, but we also pass it explicitly
        # when provided to support non-standard setups.
        client_kwargs = {}
        if self.config.api_key:
            client_kwargs["api_key"] = self.config.api_key
        if self.config.base_url:
            client_kwargs["base_url"] = self.config.base_url
        self.client = OpenAI(**client_kwargs)

    # ---------- Files ----------
    def upload_file(self, file_path: Union[str, Path]) -> str:
        """Upload a local file and return the file_id."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        with path.open("rb") as f:
            created = self.client.files.create(file=f, purpose="assistants")
        return created.id

    # ---------- Responses (Structured) ----------
    def parse_program_from_pdf(
        self,
        file_path: Union[str, Path],
        *,
        model: Optional[str] = None,
        prompt_name: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Program:
        """Upload `file_path` and parse it into a `Program` using structured output.

        Returns an instance of `models.Program` or raises if the model did not
        return a valid structure.
        """
        file_id = self.upload_file(file_path)
        return self.parse_program_from_file_id(
            file_id=file_id,
            model=model,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
        )

    def parse_program_from_file_id(
        self,
        *,
        file_id: str,
        model: Optional[str] = None,
        prompt_name: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> Program:
        """Call the Responses API with a previously uploaded file and return `Program`."""
        chosen_model = model or self.config.model

        # Load versioned prompts from files
        name = prompt_name or self.config.prompt_name
        version = prompt_version or self.config.prompt_version
        prompts = load_prompt(
            prompts_dir=self.config.prompts_dir,
            name=name,
            version=version,
        )

        # Let the SDK derive the structured-output schema from the Program model.
        response = self.client.responses.parse(
            model=chosen_model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {"type": "input_text", "text": prompts.system},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompts.user},
                        {"type": "input_file", "file_id": file_id},
                    ],
                },
            ],
            text_format=Program,
        )

        parsed = getattr(response, "output_parsed", None)
        if parsed is not None:
            return parsed

        # Fallback: attempt to validate any text blobs as JSON.
        text_chunks: list[str] = []
        for output in getattr(response, "output", []) or []:
            if getattr(output, "type", None) != "message":
                continue
            for content in getattr(output, "content", []) or []:
                if getattr(content, "type", None) != "output_text":
                    continue
                chunk = getattr(content, "text", None)
                if chunk:
                    text_chunks.append(chunk)

        if text_chunks:
            consolidated = "".join(text_chunks).strip()
            if consolidated:
                return Program.model_validate_json(consolidated)

        raise ValueError("Structured output missing from Responses API response")
