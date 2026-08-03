from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from lexicon_pipeline.audit import audit_public_release, write_audit_report
from lexicon_pipeline.config import ProjectConfig, load_config
from lexicon_pipeline.errors import PipelineError
from lexicon_pipeline.manifest import find_batch, read_manifest
from lexicon_pipeline.merging import merge_reviewed
from lexicon_pipeline.orchestration import RunMode, run_pipeline
from lexicon_pipeline.prepare import prepare_workspace
from lexicon_pipeline.rendering import render_prompts
from lexicon_pipeline.reporting import build_quality_report
from lexicon_pipeline.validation import validate_jsonl


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lexicon-pipeline")
    parser.add_argument("--config", type=Path, default=Path("project.json"))
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--provider")
    parser.add_argument("--batch-size", type=int)
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="inspect input and configuration")
    audit.add_argument("--json", action="store_true")

    prepare = sub.add_parser("prepare", help="create a manifest and safe workspace")
    prepare.add_argument("--force-reset", action="store_true")
    prepare.add_argument("--yes", action="store_true")

    sub.add_parser("render", help="render all batch prompts")

    run = sub.add_parser("run", help="run generation and/or independent review")
    run.add_argument(
        "--mode", choices=("full", "generation-only", "review-only"), default="full"
    )
    run.add_argument("--generation-only", action="store_true")
    run.add_argument("--review-only", action="store_true")
    run.add_argument("--batch", type=int)
    run.add_argument("--start-batch", type=int)

    validate = sub.add_parser("validate", help="mechanically validate an artifact")
    validate.add_argument("--path", type=Path)
    validate.add_argument("--batch", type=int)
    validate.add_argument("--stage", choices=("generated", "reviewed"), default="reviewed")

    merge = sub.add_parser("merge", help="merge valid reviewed batches only")
    merge.add_argument("--output", type=Path)
    merge.add_argument("--force-output", action="store_true")

    sub.add_parser("report", help="write JSON and Markdown quality reports")

    demo = sub.add_parser("demo", help="run the deterministic public demo")
    demo.add_argument("--reset", action="store_true")

    public = sub.add_parser("audit-public-release", help="scan a candidate public repository")
    public.add_argument("--root", type=Path, default=Path("."))
    public.add_argument("--output-dir", type=Path)

    inspect = sub.add_parser("inspect-prompt", help="show prompt version, hash, and placeholders")
    inspect.add_argument("--json", action="store_true")
    inspect.add_argument("--batch", type=int)
    inspect.add_argument("--show", action="store_true")
    for command_parser in (
        audit,
        prepare,
        run,
        validate,
        merge,
        demo,
        public,
        inspect,
    ):
        command_parser.add_argument("--config", type=Path, default=argparse.SUPPRESS)
        command_parser.add_argument("--workspace", type=Path, default=argparse.SUPPRESS)
        command_parser.add_argument("--provider", default=argparse.SUPPRESS)
        command_parser.add_argument("--batch-size", type=int, default=argparse.SUPPRESS)
    for command_parser in (sub.choices["render"], sub.choices["report"]):
        command_parser.add_argument("--config", type=Path, default=argparse.SUPPRESS)
        command_parser.add_argument("--workspace", type=Path, default=argparse.SUPPRESS)
        command_parser.add_argument("--provider", default=argparse.SUPPRESS)
        command_parser.add_argument("--batch-size", type=int, default=argparse.SUPPRESS)
    return parser


def _config(args: argparse.Namespace) -> ProjectConfig:
    config_path = args.config
    if (
        args.command == "demo"
        and config_path == Path("project.json")
        and not config_path.exists()
    ):
        config_path = Path("examples/project.demo.json")
    return load_config(
        config_path,
        workspace_override=args.workspace,
        provider_override=args.provider,
        batch_size_override=args.batch_size,
    )


def _cmd_audit(config: ProjectConfig, as_json: bool) -> int:
    checks = {
        "config": str(config.config_path),
        "words_file": config.words_file.is_file(),
        "prompt_template": config.prompt_template.is_file(),
        "review_prompt_template": config.review_prompt_template.is_file(),
        "schema_file": config.schema_file.is_file(),
        "workspace": str(config.workspace),
        "provider": config.provider,
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2) if as_json else "\n".join(
        f"{key}: {value}" for key, value in checks.items()
    ))
    return 0 if all(checks[key] for key in (
        "words_file", "prompt_template", "review_prompt_template", "schema_file"
    )) else 1


def _cmd_validate(config: ProjectConfig, args: argparse.Namespace) -> int:
    path = args.path
    expected_words: list[str] | None = None
    expected_first: int | None = None
    if args.batch is not None:
        manifest = read_manifest(config.manifest_path)
        batch = find_batch(manifest, args.batch)
        expected_words = [str(word) for word in batch["words"]]
        expected_first = int(batch["start"])
        if path is None:
            path = config.outputs_dir / f"batch_{args.batch:02d}.{args.stage}.jsonl"
    if path is None:
        raise PipelineError("validate requires --path or --batch")
    report = validate_jsonl(
        path, expected_words=expected_words, expected_first=expected_first
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.valid else 1


def _inspect_prompt(config: ProjectConfig, as_json: bool) -> int:
    from lexicon_pipeline.io_utils import sha256_file

    text = config.prompt_template.read_text(encoding="utf-8")
    markers = [
        marker
        for marker in (
            "{{WORD_LIST}}",
            "{{GENERATION_SPEC}}",
            "{{EXAMPLES}}",
            "{{START_INDEX}}",
        )
        if marker in text
    ]
    data = {
        "version": "1.0.0",
        "sha256": sha256_file(config.prompt_template),
        "placeholders": markers,
        "path": str(config.prompt_template),
    }
    print(json.dumps(data, ensure_ascii=False, indent=2) if as_json else "\n".join(
        f"{key}: {value}" for key, value in data.items()
    ))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")
    args = _parser().parse_args(argv)
    try:
        if args.command == "audit-public-release":
            result = audit_public_release(args.root)
            output = args.output_dir or (args.root / "reports")
            json_path, md_path = write_audit_report(args.root, result, output)
            print(f"{'PASS' if result.passed else 'FAIL'}: {json_path} / {md_path}")
            return 0 if result.passed else 1
        config = _config(args)
        if args.command == "audit":
            return _cmd_audit(config, args.json)
        if args.command == "prepare":
            manifest = prepare_workspace(
                config, force_reset=args.force_reset, confirmed=args.yes
            )
            print(f"prepared {len(manifest['batches'])} batches in {config.workspace}")
            return 0
        if args.command == "render":
            print(f"rendered {len(render_prompts(config))} prompts")
            return 0
        if args.command == "run":
            if args.generation_only and args.review_only:
                raise PipelineError("choose only one of --generation-only and --review-only")
            mode: RunMode
            if args.generation_only:
                mode = "generation-only"
            elif args.review_only:
                mode = "review-only"
            else:
                mode = cast(RunMode, args.mode)
            manifest = run_pipeline(
                config,
                mode=mode,
                selected_batch=args.batch,
                start_batch=args.start_batch,
            )
            print(json.dumps({"states": [item["state"] for item in manifest["batches"]]}))
            return 0
        if args.command == "validate":
            return _cmd_validate(config, args)
        if args.command == "merge":
            path, count = merge_reviewed(
                config, args.output, overwrite=args.force_output
            )
            print(f"merged {count} reviewed records into {path}")
            return 0
        if args.command == "report":
            json_path, md_path, data = build_quality_report(config)
            status = "PASS" if data["mechanical_validation_passed"] else "FAIL"
            print(f"{status}: {json_path} / {md_path}")
            return 0 if data["mechanical_validation_passed"] else 1
        if args.command == "demo":
            prepare_workspace(config, force_reset=args.reset, confirmed=args.reset)
            render_prompts(config)
            run_pipeline(config)
            merged, count = merge_reviewed(config, overwrite=args.reset)
            build_quality_report(config)
            print(f"synthetic demo PASS: {count} records in {merged}")
            return 0
        if args.command == "inspect-prompt":
            if args.batch is not None:
                prompt_path = config.prompts_dir / f"batch_{args.batch:02d}.prompt.txt"
                if not prompt_path.is_file():
                    raise PipelineError(f"rendered prompt does not exist: {prompt_path}")
                if args.show:
                    print(prompt_path.read_text(encoding="utf-8"))
                    return 0
            return _inspect_prompt(config, args.json)
        raise PipelineError(f"unsupported command: {args.command}")
    except (PipelineError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
