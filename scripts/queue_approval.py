#!/usr/bin/env python3
"""Append a pending approval request to .claude-loop/approval-queue.md.

Usage:
    python scripts/queue_approval.py --target <root> --title "Push branch" \
        --action "git push origin my-branch" --reason "ready for review" \
        --risk "publishes the branch" --risk-level low
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import append_text, now_stamp, require_vault  # noqa: E402

ENTRY = """
## [pending] {title}
- **Requested:** {stamp}
- **Action:** {action}
- **Reason:** {reason}
- **Risk:** {level} — {risk}
- **Status:** pending
"""


def main():
    ap = argparse.ArgumentParser(description="Queue an approval request.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    ap.add_argument("--title", required=True, help="short title for the request")
    ap.add_argument("--action", required=True, help="the exact action awaiting approval")
    ap.add_argument("--reason", required=True, help="why it should be approved")
    ap.add_argument("--risk", required=True, help="what could go wrong / blast radius")
    ap.add_argument(
        "--risk-level", default="medium", choices=["low", "medium", "high"], help="risk level"
    )
    args = ap.parse_args()

    vault = require_vault(args.target)
    queue = vault / "approval-queue.md"

    append_text(
        queue,
        ENTRY.format(
            title=args.title.strip(),
            stamp=now_stamp(),
            action=args.action.strip(),
            reason=args.reason.strip(),
            level=args.risk_level,
            risk=args.risk.strip(),
        ),
    )
    print("Queued approval: '{}' [{}]".format(args.title, args.risk_level))
    print("  -> {}".format(queue))
    print("Tell the user it's queued; continue with non-gated work until they answer.")


if __name__ == "__main__":
    main()
