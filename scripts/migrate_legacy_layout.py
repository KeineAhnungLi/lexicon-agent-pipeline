from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lexicon_pipeline.io_utils import atomic_write_text


def migrate(source: Path, destination: Path) -> None:
    """Translate safe configuration keys only; never copy source data or outputs."""
    legacy: dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
    public = {
        "project_name": "migrated_project",
        "repository_root": ".",
        "input_file": "private/input.tsv",
        "batch_size": int(legacy.get("batch_size", 200)),
        "start_index": int(legacy.get("start_index", 1)),
        "prompt_template": "prompts/prompt_template.md",
        "review_prompt_template": "prompts/review_prompt_template.md",
        "generation_spec": "prompts/generation_spec.md",
        "examples": "private/examples.jsonl",
        "workspace": "workspace/migrated",
        "output_dir": "outputs/migrated",
        "final_filename": "lexicon.ai-reviewed.jsonl",
        "agent_schema_file": "schemas/lexicon_agent_record.schema.json",
        "schema_file": "schemas/lexicon_record.schema.json",
        "agent_expected_fields": 29,
        "expected_fields": 30,
        "provider": "codex-cli",
        "provider_options": {"executable": "codex", "timeout_seconds": 1800, "extra_args": []},
    }
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    atomic_write_text(
        destination,
        json.dumps(public, ensure_ascii=False, indent=2) + "\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate legacy configuration keys without copying private artifacts."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    migrate(args.source, args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
