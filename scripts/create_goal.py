#!/usr/bin/env python3
"""Create a goal card in .claude-loop/goals/<slug>.md.

Usage:
    python scripts/create_goal.py --target <root> --title "Ship X" \
        --objective "..." \
        --criteria "first done criterion" "second" \
        --verify "exact step/command that proves it"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import require_vault, slugify, today, write_text  # noqa: E402

TEMPLATE = """# Goal: {title}

- **Slug:** {slug}
- **Status:** active        <!-- active | blocked | done | abandoned -->
- **Created:** {date}
- **Updated:** {date}

## Objective
{objective}

## Done criteria
{criteria}

## Verification
{verify}
"""


def bullets(items, placeholder):
    items = [i for i in (items or []) if i.strip()]
    if not items:
        return "- [ ] {}".format(placeholder)
    return "\n".join("- [ ] {}".format(i.strip()) for i in items)


def main():
    ap = argparse.ArgumentParser(description="Create a goal card.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    ap.add_argument("--title", required=True, help="goal title")
    ap.add_argument("--slug", help="override the auto-generated slug")
    ap.add_argument("--objective", default="", help="one-paragraph objective")
    ap.add_argument("--criteria", nargs="*", default=[], help="done-criteria, one per arg")
    ap.add_argument("--verify", nargs="*", default=[], help="verification steps, one per arg")
    ap.add_argument("--force", action="store_true", help="overwrite if the card already exists")
    args = ap.parse_args()

    vault = require_vault(args.target)
    slug = slugify(args.slug or args.title)
    dest = vault / "goals" / (slug + ".md")
    if dest.exists() and not args.force:
        raise SystemExit("error: goal already exists: {} (use --force to overwrite)".format(dest))

    content = TEMPLATE.format(
        title=args.title,
        slug=slug,
        date=today(),
        objective=args.objective.strip() or "_(describe what success looks like and why it matters)_",
        criteria=bullets(args.criteria, "_(add a concrete, checkable criterion)_"),
        verify=bullets(args.verify, "_(the exact step/command that proves a criterion — run it before checking)_"),
    )
    write_text(dest, content)
    print("Created goal: {}".format(dest))
    print("Status: active  ·  criteria: {}".format(max(1, len([c for c in args.criteria if c.strip()]))))


if __name__ == "__main__":
    main()
