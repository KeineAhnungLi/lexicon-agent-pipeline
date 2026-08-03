from __future__ import annotations

import sys
from pathlib import Path

from lexicon_pipeline.audit import audit_public_release, write_audit_report


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    result = audit_public_release(root)
    write_audit_report(root, result, root / "reports")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
