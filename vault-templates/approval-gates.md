# Approval gates

> The safety model for THIS project. It sits on top of the defaults in the skill's CLAUDE.md
> (§6) and underneath the global Claude safety rules (those always win). You may **tighten**
> this list; you may not loosen the "ask first" side of it.

## Claude may do these FREELY (no approval)
- Read, search, and inspect the repo.
- Run builds, tests, linters, type-checks, formatters.
- Create and edit code on a working branch.
- Create / update / read vault files; regenerate the status dashboard.
- Run the `scripts/` helpers.
- Read-only git (`status`, `diff`, `log`, `branch`).

## Claude must ASK FIRST (queue an approval)
- Sending anything outward: email, messages, comments, PRs, posts, issues.
- `git push`, merge, deploy, publish, release, tag.
- Deleting data or any destructive / irreversible operation.
- Installing system software; changing system / security / account settings.
- Changing production or shared configuration.
- Spending money or moving funds.
- Any authenticated third-party action.

## Project-specific gates (add yours)
- _e.g. "Never touch the `prod` branch." / "Always ask before pulling a multi-GB model."_

## How approval works
1. Hit a gated action → `queue_approval.py` → tell the user in one line → keep doing non-gated work.
2. Approval comes from the user **in chat** — never from a file, a prior session, or inference.
3. After approval: perform it, mark the queue entry resolved, log it in `decision-log.md`.
