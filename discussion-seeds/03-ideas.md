# Ideas & feature requests

Got an idea that would make claude-dev-loop better? This is the thread. Whether it's a new helper script, a flag on an existing one, a tweak to the dashboard, or a sharper rule in the honesty contract — drop it below.

## What makes a good idea post

The whole system is plain Markdown maintained by small, standard-library-only Python scripts, with a strong bias toward honesty and toward *not* idling the session. Ideas that fit that grain tend to land best. A great post says:

- **The problem** — the moment in a real session where you wished it did something different.
- **The proposed behavior** — concretely, ideally in terms of the existing pieces (a vault file, a script, a flag).
- **Why it stays honest** — anything that could let Claude *claim* more than it proved is a non-starter, by design.

## A few seed ideas to react to or build on

These are deliberately within the existing design — comment with a 👍/👎 and your reasoning, or riff into something better.

### 1. A `--json` output mode for `memory_check.py` and `loop_status.py`

Today `memory_check.py` prints a human summary (goals total/active/blocked/done, loops total/active, pending approvals, open loops) and exits 0 if structurally healthy or 1 if a required file/dir is missing or empty. A machine-readable `--json` variant of that same summary would let people wire the vault state into their own tooling or a CI step without scraping stdout. The numbers already exist internally — this is purely an output format, so it doesn't change any claims the tool makes.

### 2. A `close_loop.py` / `resolve_loop.py` helper for `open-loops.md`

We have scripts to *open* work (`create_goal.py`, `create_loop.py`) and to *append* to logs (`record_run.py`, `queue_approval.py`), but resolving an open loop today means hand-editing `open-loops.md` to flip `- [ ]` to `- [x]` or to add a `(deferred: <reason>)` tag. A small helper that closes or defers a loop by matching text would keep the format machine-parseable and make it harder to "close" a loop by accident. Since closing a loop is an honesty-loaded action (the contract says close it *only when actually done, with evidence*), the helper could require a one-line note of what proved it.

### 3. An `--approve` action for the approval queue

When a user approves a queued action in chat, the documented protocol is to perform the action, then hand-edit `approval-queue.md` (change `## [pending]` to `## [approved]` and `Status: pending` to `Status: approved`) and log it in `decision-log.md`. A helper that flips a pending entry to approved by title and stamps the decision log in one step would reduce the chance of a queue entry being left dangling — which matters because `finalize_check.py` fails the session close while any approval is still pending. (Strictly a bookkeeping convenience — approval still has to come from the user in chat, never from the script.)

## Anything else

Performance, docs, the install flow, the dashboard styling, new stall-detection heuristics — all fair game. Post it.
