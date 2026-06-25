#!/usr/bin/env python3
"""Initialize a .claude-loop/ vault in a target project.

Creates the directory structure and copies the starter templates. Existing files
are left untouched (skipped), so it is safe to re-run.

Usage:
    python scripts/bootstrap_vault.py --target <project-root>
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    REQUIRED_DIRS,
    target_root,
    templates_dir,
    today,
    vault_dir,
    write_text,
)

# The six template files copied from vault-templates/ into the vault root.
TEMPLATE_FILES = [
    "project-brief.md",
    "preferences.md",
    "approval-gates.md",
    "approval-queue.md",
    "open-loops.md",
    "automation-registry.md",
]

DECISION_LOG_HEADER = """# Decision log

Append-only record of notable, hard-to-reverse, or surprising-in-hindsight decisions.

Format for each entry:

## {date} — <short title>
- **Context:** <what prompted it>
- **Decision:** <what was chosen>
- **Rationale:** <why; what was rejected and why>
""".format(date=today())


def stub_for(name):
    title = name.replace(".md", "").replace("-", " ").title()
    return "# {}\n\n_(starter template was not found at install time; fill this in)_\n".format(title)


def main():
    ap = argparse.ArgumentParser(description="Bootstrap a .claude-loop vault.")
    ap.add_argument("--target", required=True, help="project root to create the vault in")
    args = ap.parse_args()

    root = target_root(args.target)
    if not root.is_dir():
        raise SystemExit("error: target is not a directory: {}".format(root))

    vault = vault_dir(args.target)
    created, skipped = [], []

    # Directories
    vault.mkdir(parents=True, exist_ok=True)
    for d in REQUIRED_DIRS:
        sub = vault / d
        if sub.is_dir():
            skipped.append(str(sub.relative_to(root)))
        else:
            sub.mkdir(parents=True, exist_ok=True)
            created.append(str(sub.relative_to(root)) + "/")
        # keep empty dirs in git
        keep = sub / ".gitkeep"
        if not keep.exists():
            write_text(keep, "")

    tdir = templates_dir()

    # Template files (copied, never overwritten)
    for name in TEMPLATE_FILES:
        dest = vault / name
        if dest.exists():
            skipped.append(str(dest.relative_to(root)))
            continue
        src = (tdir / name) if tdir else None
        if src and src.exists():
            content = src.read_text(encoding="utf-8")
        else:
            content = stub_for(name)
        write_text(dest, content)
        created.append(str(dest.relative_to(root)))

    # Decision log (created directly, not a template)
    dlog = vault / "decision-log.md"
    if dlog.exists():
        skipped.append(str(dlog.relative_to(root)))
    else:
        write_text(dlog, DECISION_LOG_HEADER)
        created.append(str(dlog.relative_to(root)))

    print("Vault: {}".format(vault))
    if tdir is None:
        print("warning: vault-templates/ not found; wrote minimal stubs instead.")
    print("\nCreated ({}):".format(len(created)))
    for c in created:
        print("  + {}".format(c))
    if skipped:
        print("\nSkipped (already present) ({}):".format(len(skipped)))
        for s in skipped:
            print("  = {}".format(s))
    print("\nNext: python scripts/memory_check.py --target {}".format(args.target))


if __name__ == "__main__":
    main()
