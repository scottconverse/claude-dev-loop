#!/usr/bin/env python3
"""Pre-session-close gate for a .claude-loop/ vault.

FAILS (exit 1) if any of these are true:
  - there are pending approvals the user hasn't answered;
  - there is an active goal with zero completed criteria (work opened, nothing proven);
  - there are unresolved open loops (un-deferred '- [ ]' items in open-loops.md).

A clean pass (exit 0) is the only honest way to call a session done.

Usage:
    python scripts/finalize_check.py --target <root>
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    goal_files,
    load_goal,
    open_loops,
    pending_approvals,
    require_vault,
)


def main():
    ap = argparse.ArgumentParser(description="Finalize (session-close) gate.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    args = ap.parse_args()

    vault = require_vault(args.target)
    failures = []

    # 1. Pending approvals
    pending = pending_approvals(vault)
    if pending:
        failures.append("{} pending approval(s) unanswered:".format(len(pending)))
        for t in pending:
            failures.append("    - {}".format(t))

    # 2. Active goals with zero completed criteria
    goals = [load_goal(p) for p in goal_files(vault)]
    unstarted = [g for g in goals if g["status"] == "active" and g["checked"] == 0]
    if unstarted:
        failures.append("{} active goal(s) with 0 completed criteria:".format(len(unstarted)))
        for g in unstarted:
            failures.append("    - {} ({}/{} criteria)".format(g["title"], g["checked"], g["total"]))

    # 3. Unresolved open loops
    unresolved, _deferred = open_loops(vault)
    if unresolved:
        failures.append("{} unresolved open loop(s) (resolve, or tag '(deferred: reason)'):".format(
            len(unresolved)))
        for d in unresolved:
            failures.append("    - {}".format(d))

    print("Finalize check: {}".format(vault))
    print("-" * 56)
    if failures:
        print("NOT READY TO CLOSE:")
        for f in failures:
            print("  " + f if f.startswith("    ") else "  x " + f)
        print("-" * 56)
        print("Result: FAIL")
        sys.exit(1)

    print("  - no pending approvals")
    print("  - every active goal has at least one proven criterion")
    print("  - no unresolved open loops")
    print("-" * 56)
    print("Result: PASS — safe to close. (Regenerate status.html before you go.)")
    sys.exit(0)


if __name__ == "__main__":
    main()
