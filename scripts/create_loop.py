#!/usr/bin/env python3
"""Create a loop spec in .claude-loop/loops/<slug>.md and register it.

Also seeds the loop's run log header and appends an entry to automation-registry.md.

Usage:
    python scripts/create_loop.py --target <root> --title "Nightly test gate" \
        --trigger "..." --action "..." --verifier "..." \
        --budget "5 runs" --stop "green build or escalate after 3 failures"
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import append_text, read_text, require_vault, slugify, today, write_text  # noqa: E402

TEMPLATE = """# Loop: {title}

- **Slug:** {slug}
- **Status:** active        <!-- active | paused | done -->
- **Created:** {date}
- **Budget:** {budget}

## Trigger
{trigger}

## Action
{action}

## Verifier
{verifier}

## Stop condition
{stop}
"""

RUNLOG_HEADER = """# Run log — {slug}

Append-only. Newest entries at the bottom. Add entries with:
`python scripts/record_run.py --target <root> --loop {slug} ...`
"""


def or_placeholder(value, text):
    return value.strip() if value and value.strip() else "_({})_".format(text)


def main():
    ap = argparse.ArgumentParser(description="Create a loop spec.")
    ap.add_argument("--target", required=True, help="project root containing the vault")
    ap.add_argument("--title", required=True, help="loop title")
    ap.add_argument("--slug", help="override the auto-generated slug")
    ap.add_argument("--trigger", default="", help="when the loop runs")
    ap.add_argument("--action", default="", help="what it does each iteration")
    ap.add_argument("--verifier", default="", help="runnable success check per iteration")
    ap.add_argument("--budget", default="until done criteria met", help="resource budget")
    ap.add_argument("--stop", default="", help="stop condition")
    ap.add_argument("--force", action="store_true", help="overwrite if the loop already exists")
    args = ap.parse_args()

    vault = require_vault(args.target)
    slug = slugify(args.slug or args.title)
    dest = vault / "loops" / (slug + ".md")
    if dest.exists() and not args.force:
        raise SystemExit("error: loop already exists: {} (use --force to overwrite)".format(dest))

    content = TEMPLATE.format(
        title=args.title,
        slug=slug,
        date=today(),
        budget=args.budget.strip() or "until done criteria met",
        trigger=or_placeholder(args.trigger, "when this loop should run"),
        action=or_placeholder(args.action, "what you do on each iteration — concrete and bounded"),
        verifier=or_placeholder(args.verifier, "the objective, runnable check for each iteration"),
        stop=or_placeholder(args.stop, "success, budget exhausted, or escalate"),
    )
    write_text(dest, content)

    # Seed the run log so record_run has a place to append.
    runlog = vault / "runs" / (slug + "-runs.md")
    if not runlog.exists():
        write_text(runlog, RUNLOG_HEADER.format(slug=slug))

    # Register in automation-registry.md (idempotent: skip if slug already listed).
    registry = vault / "automation-registry.md"
    reg_text = read_text(registry)
    if "`{}`".format(slug) not in reg_text:
        append_text(
            registry,
            "\n- **{title}** (`{slug}`) — registered {date} · status: active\n".format(
                title=args.title, slug=slug, date=today()
            ),
        )

    print("Created loop: {}".format(dest))
    print("Run log:      {}".format(runlog))
    print("Registered in automation-registry.md")


if __name__ == "__main__":
    main()
