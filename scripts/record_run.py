#!/usr/bin/env python3
"""Append a run entry to a loop's run log (.claude-loop/runs/<loop>-runs.md).

Usage:
    python scripts/record_run.py --target <root> --loop <loop-slug> \
        --observed "what you saw" --action "what you did" \
        --result "PASS/FAIL + the real verifier result" --next "the next step"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import append_text, now_stamp, require_vault, slugify, write_text  # noqa: E402

ENTRY = """
## {stamp}
- **Observed:** {observed}
- **Action:** {action}
- **Verifier:** {result}
- **Next:** {next}
"""

HEADER = "# Run log — {slug}\n\nAppend-only. Newest entries at the bottom.\n"


def main():
    ap = argparse.ArgumentParser(description="Append a loop run entry.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    ap.add_argument("--loop", required=True, help="loop slug this run belongs to")
    ap.add_argument("--observed", required=True, help="the state you actually saw")
    ap.add_argument("--action", required=True, help="what you did")
    ap.add_argument("--result", required=True, help="the REAL verifier result (incl. failures)")
    ap.add_argument("--next", dest="next_step", default="none", help="the next step")
    args = ap.parse_args()

    vault = require_vault(args.target)
    slug = slugify(args.loop)
    runlog = vault / "runs" / (slug + "-runs.md")
    if not runlog.exists():
        write_text(runlog, HEADER.format(slug=slug))

    append_text(
        runlog,
        ENTRY.format(
            stamp=now_stamp(),
            observed=args.observed.strip(),
            action=args.action.strip(),
            result=args.result.strip(),
            next=args.next_step.strip() or "none",
        ),
    )
    print("Recorded run for '{}' at {}".format(slug, now_stamp()))
    print("  -> {}".format(runlog))


if __name__ == "__main__":
    main()
