#!/usr/bin/env python3
"""Health-check a .claude-loop/ vault.

Reports missing or empty required files, active goal count, pending approvals,
and open-loop count. Warns when open loops exceed 5.

Exit code: 0 if the vault is structurally healthy (all required files/dirs present
and non-empty), 1 otherwise. Warnings alone do not fail.

Usage:
    python scripts/memory_check.py --target <root>
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    REQUIRED_DIRS,
    REQUIRED_FILES,
    goal_files,
    load_goal,
    load_loop,
    loop_files,
    open_loops,
    pending_approvals,
    read_text,
    vault_dir,
)

OPEN_LOOP_WARN = 5


def main():
    ap = argparse.ArgumentParser(description="Vault health check.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    args = ap.parse_args()

    vault = vault_dir(args.target)
    problems = []
    warnings = []

    print("Vault health check: {}".format(vault))
    print("-" * 56)

    if not vault.is_dir():
        print("MISSING: vault not found. Run bootstrap_vault.py first.")
        return sys.exit(1)

    # Required dirs
    for d in REQUIRED_DIRS:
        if not (vault / d).is_dir():
            problems.append("missing dir: {}/".format(d))

    # Required files (present + non-empty)
    for f in REQUIRED_FILES:
        p = vault / f
        if not p.exists():
            problems.append("missing file: {}".format(f))
        elif not read_text(p).strip():
            problems.append("empty file: {}".format(f))

    # Goals
    goals = [load_goal(p) for p in goal_files(vault)]
    active = [g for g in goals if g["status"] == "active"]
    done = [g for g in goals if g["status"] == "done"]
    blocked = [g for g in goals if g["status"] == "blocked"]

    # Loops
    loops = [load_loop(p, vault) for p in loop_files(vault)]
    active_loops = [l for l in loops if l["status"] == "active"]

    # Approvals + open loops
    pending = pending_approvals(vault)
    unresolved, deferred = open_loops(vault)

    if len(unresolved) > OPEN_LOOP_WARN:
        warnings.append(
            "open loops = {} (> {}): you're spreading thin — finish or consolidate.".format(
                len(unresolved), OPEN_LOOP_WARN
            )
        )

    print("Goals:      {} total · {} active · {} blocked · {} done".format(
        len(goals), len(active), len(blocked), len(done)))
    print("Loops:      {} total · {} active".format(len(loops), len(active_loops)))
    print("Approvals:  {} pending".format(len(pending)))
    for t in pending:
        print("              - {}".format(t))
    print("Open loops: {} unresolved · {} deferred".format(len(unresolved), len(deferred)))
    for d in unresolved:
        print("              - {}".format(d))

    print("-" * 56)
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print("  ! {}".format(w))
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  x {}".format(p))
        print("\nResult: UNHEALTHY ({} problem(s))".format(len(problems)))
        sys.exit(1)

    print("Result: HEALTHY" + ("  ({} warning(s))".format(len(warnings)) if warnings else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
